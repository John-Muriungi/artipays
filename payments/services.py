import base64
import logging
import re
from decimal import Decimal, InvalidOperation

import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from redis.exceptions import RedisError

from music_requests.models import SongRequest, Tip
from .models import Transaction

logger = logging.getLogger(__name__)


class PaymentError(Exception):
    pass


def _notify_artist_of_paid_request(artist_id):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        logger.warning("No channel layer configured; artist request notification was skipped.")
        return
    try:
        async_to_sync(channel_layer.group_send)(
            f"artist_{artist_id}",
            {
                "type": "artist.notification",
                "payload": {"type": "paid_request"},
            },
        )
    except (OSError, RedisError, RuntimeError) as exc:
        logger.error("Could not publish paid request notification: %s", exc)


def normalize_phone(phone):
    digits = re.sub(r"\D", "", phone or "")
    if digits.startswith("0") and len(digits) == 10:
        digits = "254" + digits[1:]
    elif digits.startswith("7") and len(digits) == 9:
        digits = "254" + digits
    if not re.fullmatch(r"254[17]\d{8}", digits):
        raise ValueError("Enter a valid Kenyan mobile number.")
    return digits


def _base_url():
    if settings.MPESA_ENVIRONMENT == "production":
        return "https://api.safaricom.co.ke"
    return "https://sandbox.safaricom.co.ke"


def _credentials():
    required = (
        settings.MPESA_CONSUMER_KEY,
        settings.MPESA_CONSUMER_SECRET,
        settings.MPESA_SHORTCODE,
        settings.MPESA_PASSKEY,
        settings.MPESA_CALLBACK_URL,
    )
    if not all(required):
        raise PaymentError("M-Pesa credentials and callback URL must be configured.")
    return required


def _access_token():
    key, secret, *_ = _credentials()
    try:
        response = requests.get(
            f"{_base_url()}/oauth/v1/generate?grant_type=client_credentials",
            auth=(key, secret),
            timeout=settings.MPESA_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        token = response.json().get("access_token")
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Daraja access token request failed: %s", exc)
        raise PaymentError("Payment provider authentication failed.") from exc
    if not token:
        raise PaymentError("Payment provider returned no access token.")
    return token


def _password_and_timestamp(shortcode, passkey):
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    raw = f"{shortcode}{passkey}{timestamp}".encode()
    return base64.b64encode(raw).decode(), timestamp


def initiate_stk_push(payment):
    shortcode, passkey = settings.MPESA_SHORTCODE, settings.MPESA_PASSKEY
    _credentials()
    password, timestamp = _password_and_timestamp(shortcode, passkey)
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": settings.MPESA_TRANSACTION_TYPE,
        "Amount": payment.amount,
        "PartyA": payment.phone_number,
        "PartyB": shortcode,
        "PhoneNumber": payment.phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": f"ARTIPAY-{str(payment.public_id)[:12]}",
        "TransactionDesc": "Paid song request" if payment.transaction_type == Transaction.Type.SONG_REQUEST else "Artist tip",
    }
    try:
        response = requests.post(
            f"{_base_url()}/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers={"Authorization": f"Bearer {_access_token()}"},
            timeout=settings.MPESA_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Daraja STK push failed: %s", exc)
        raise PaymentError("Payment provider could not initiate the payment.") from exc
    if data.get("ResponseCode") != "0" or not data.get("CheckoutRequestID"):
        raise PaymentError(data.get("errorMessage") or data.get("ResponseDescription") or "STK push was rejected.")
    return data


def verify_stk_payment(checkout_request_id):
    shortcode, passkey = settings.MPESA_SHORTCODE, settings.MPESA_PASSKEY
    _credentials()
    password, timestamp = _password_and_timestamp(shortcode, passkey)
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id,
    }
    try:
        response = requests.post(
            f"{_base_url()}/mpesa/stkpushquery/v1/query",
            json=payload,
            headers={"Authorization": f"Bearer {_access_token()}"},
            timeout=settings.MPESA_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.exception("Daraja STK verification failed")
        raise PaymentError("Unable to verify the payment with M-Pesa.") from exc


def _callback_metadata(callback):
    body = callback.get("Body", {}).get("stkCallback", {})
    metadata = body.get("CallbackMetadata", {}).get("Item", [])
    values = {item.get("Name"): item.get("Value") for item in metadata}
    return body, values


def process_mpesa_callback(callback):
    body, _ = _callback_metadata(callback)
    checkout_id = body.get("CheckoutRequestID")
    if not checkout_id:
        raise PaymentError("Callback is missing CheckoutRequestID.")
    with transaction.atomic():
        payment = Transaction.objects.select_for_update().filter(checkout_request_id=checkout_id).first()
        if payment is None:
            logger.warning("Ignoring callback for unknown M-Pesa checkout ID %s", checkout_id)
            raise PaymentError("Unknown payment reference.")
        payment.callback_data = callback
        if payment.status != Transaction.Status.PENDING:
            payment.save(update_fields=["callback_data", "updated_at"])
            return payment

    # Callback data is untrusted; query Daraja before accepting either success or failure.
    verified = verify_stk_payment(checkout_id)
    verified_code = verified.get("ResultCode")
    if verified_code is None:
        return payment
    verified_code = str(verified_code)
    with transaction.atomic():
        payment = Transaction.objects.select_for_update().get(pk=payment.pk)
        if payment.status != Transaction.Status.PENDING:
            return payment
        payment.result_code = verified_code
        payment.result_description = str(verified.get("ResultDesc", ""))[:255]
        payment.verification_data = verified
        if verified_code != "0":
            payment.status = (
                Transaction.Status.CANCELLED
                if verified_code in {"1032", "1037"}
                else Transaction.Status.FAILED
            )
            payment.save()
            return payment
        _, verified_values = _callback_metadata(
            {"Body": {"stkCallback": {"CallbackMetadata": verified.get("CallbackMetadata", {})}}}
        )
        # STK query confirms the checkout status; its response commonly omits metadata.
        # In that case compare callback metadata with the expected transaction values.
        _, callback_values = _callback_metadata(callback)
        verified_values = verified_values or callback_values
        receipt = str(verified_values.get("MpesaReceiptNumber", ""))
        verified_amount = verified_values.get("Amount")
        verified_phone = str(verified_values.get("PhoneNumber", ""))
        try:
            amount_matches = Decimal(str(verified_amount)) == Decimal(payment.amount)
        except (InvalidOperation, TypeError):
            amount_matches = False
        if (
            not receipt
            or verified_amount is None
            or not amount_matches
            or verified_phone != payment.phone_number
        ):
            payment.status = Transaction.Status.FAILED
            payment.result_description = "Verified provider details did not match this payment."
            payment.save()
            return payment
        if Transaction.objects.filter(provider_receipt=receipt).exclude(pk=payment.pk).exists():
            payment.status = Transaction.Status.FAILED
            payment.result_description = "M-Pesa receipt is already linked to another payment."
            payment.save()
            return payment
        payment.status = Transaction.Status.SUCCESS
        payment.provider_receipt = receipt
        payment.save()
        if payment.song_request_id:
            SongRequest.objects.filter(
                pk=payment.song_request_id, status=SongRequest.Status.AWAITING_PAYMENT
            ).update(status=SongRequest.Status.PENDING)
            transaction.on_commit(
                lambda artist_id=payment.artist_id: _notify_artist_of_paid_request(artist_id)
            )
        if payment.tip_id:
            Tip.objects.filter(pk=payment.tip_id).update(paid=True)
        return payment

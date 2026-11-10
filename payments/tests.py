from datetime import date, time
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import ArtistProfile
from events.models import Event
from music_requests.models import SongRequest
from payments.models import Transaction
from payments.services import PaymentError, process_mpesa_callback

User = get_user_model()


class CallbackTests(TestCase):
    def setUp(self):
        artist = User.objects.create_user("dj", email="dj@example.com", password="Strong-password-24!")
        ArtistProfile.objects.create(user=artist, stage_name="DJ Test", phone="254712345678")
        event = Event.objects.create(
            artist=artist,
            name="Friday Live",
            event_date=date(2027, 5, 1),
            start_time=time(20, 0),
            song_request_price=200,
            status=Event.Status.ACTIVE,
        )
        request = SongRequest.objects.create(
            event=event,
            artist=artist,
            song_title="One Dance",
            song_artist="Drake",
            amount=200,
            status=SongRequest.Status.AWAITING_PAYMENT,
        )
        self.payment = Transaction.objects.create(
            artist=artist,
            event=event,
            song_request=request,
            transaction_type=Transaction.Type.SONG_REQUEST,
            amount=200,
            phone_number="254712345678",
            checkout_request_id="checkout-1",
            merchant_request_id="merchant-1",
        )
        self.callback = {
            "Body": {
                "stkCallback": {
                    "CheckoutRequestID": "checkout-1",
                    "ResultCode": 0,
                    "ResultDesc": "Success",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": 200},
                            {"Name": "MpesaReceiptNumber", "Value": "ABC123"},
                            {"Name": "PhoneNumber", "Value": 254712345678},
                        ]
                    },
                }
            }
        }

    @patch("payments.services.verify_stk_payment")
    def test_verified_success_marks_request_paid_and_callback_is_idempotent(self, verify):
        verify.return_value = {"ResultCode": 0, "ResultDesc": "The service request is processed successfully"}
        with patch("payments.services._notify_artist_of_paid_request") as notify:
            with self.captureOnCommitCallbacks(execute=True):
                payment = process_mpesa_callback(self.callback)
            notify.assert_called_once_with(payment.artist_id)
        self.assertEqual(payment.status, Transaction.Status.SUCCESS)
        payment.song_request.refresh_from_db()
        self.assertEqual(payment.song_request.status, SongRequest.Status.PENDING)
        self.assertEqual(payment.provider_receipt, "ABC123")
        process_mpesa_callback(self.callback)
        self.assertEqual(Transaction.objects.count(), 1)
        verify.assert_called_once()

    @patch("payments.services.verify_stk_payment")
    def test_unverified_or_failed_callback_never_exposes_request(self, verify):
        verify.return_value = {"ResultCode": 1032, "ResultDesc": "Request cancelled by user"}
        payment = process_mpesa_callback(self.callback)
        self.assertEqual(payment.status, Transaction.Status.CANCELLED)
        payment.song_request.refresh_from_db()
        self.assertEqual(payment.song_request.status, SongRequest.Status.AWAITING_PAYMENT)

    def test_unknown_callback_reference_is_rejected(self):
        callback = {"Body": {"stkCallback": {"CheckoutRequestID": "unknown"}}}
        with self.assertRaises(PaymentError):
            process_mpesa_callback(callback)

    @patch("payments.services.verify_stk_payment")
    def test_verified_payment_with_mismatched_amount_is_not_credited(self, verify):
        callback = {
            **self.callback,
            "Body": {
                "stkCallback": {
                    **self.callback["Body"]["stkCallback"],
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": 1},
                            {"Name": "MpesaReceiptNumber", "Value": "FAKE1"},
                            {"Name": "PhoneNumber", "Value": 254712345678},
                        ]
                    },
                }
            },
        }
        verify.return_value = {"ResultCode": 0, "ResultDesc": "Success"}
        payment = process_mpesa_callback(callback)
        self.assertEqual(payment.status, Transaction.Status.FAILED)
        payment.song_request.refresh_from_db()
        self.assertEqual(payment.song_request.status, SongRequest.Status.AWAITING_PAYMENT)

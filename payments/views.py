import json
import logging

from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Transaction
from .services import PaymentError, process_mpesa_callback

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def mpesa_callback(request):
    if len(request.body) > 65536:
        return HttpResponseBadRequest("Invalid callback.")
    try:
        payload = json.loads(request.body)
        process_mpesa_callback(payload)
    except (json.JSONDecodeError, PaymentError, TypeError, ValueError) as exc:
        logger.warning("Rejected M-Pesa callback: %s", exc)
        return HttpResponseBadRequest("Invalid callback.")
    return HttpResponse("Accepted")


@require_GET
def payment_status(request, public_id):
    payment = get_object_or_404(Transaction, public_id=public_id)
    return render(request, "payments/status.html", {"payment": payment})


@require_GET
def payment_status_json(request, public_id):
    payment = get_object_or_404(Transaction, public_id=public_id)
    response = {"status": payment.status, "description": payment.result_description}
    if payment.status == Transaction.Status.SUCCESS:
        response["confirmation_url"] = reverse(
            "payments:confirmation", kwargs={"public_id": payment.public_id}
        )
    return JsonResponse(response)


@require_GET
def payment_confirmation(request, public_id):
    payment = get_object_or_404(
        Transaction.objects.select_related("event", "event__artist", "song_request", "tip"),
        public_id=public_id,
        status=Transaction.Status.SUCCESS,
    )
    return render(request, "payments/confirmation.html", {"payment": payment})

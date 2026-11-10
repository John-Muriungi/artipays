from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from events.models import Event
from payments.models import Transaction
from payments.services import PaymentError, initiate_stk_push

from .forms import SongRequestForm, TipForm
from .models import SongRequest, Tip


def _create_payment(request, event, form, *, kind):
    data = form.cleaned_data
    if event.status != Event.Status.ACTIVE:
        form.add_error(None, "This event is not accepting payments.")
        return None
    if kind == Transaction.Type.SONG_REQUEST:
        tip_amount = data.get("tip_amount") or 0
        if tip_amount and tip_amount < event.minimum_tip:
            form.add_error("tip_amount", f"Tip must be at least KES {event.minimum_tip}.")
            return None
        item = SongRequest.objects.create(
            event=event,
            artist=event.artist,
            requester_name=data["requester_name"],
            song_title=data["song_title"],
            song_artist=data["song_artist"],
            message=data["message"],
            amount=event.song_request_price,
            tip_amount=tip_amount,
        )
        amount = event.song_request_price + tip_amount
    else:
        if data["amount"] < max(event.minimum_tip, 1):
            form.add_error("amount", f"Tip must be at least KES {max(event.minimum_tip, 1)}.")
            return None
        item = Tip.objects.create(
            event=event,
            artist=event.artist,
            requester_name=data["requester_name"],
            amount=data["amount"],
            message=data["message"],
        )
        amount = data["amount"]
    transaction = Transaction.objects.create(
        artist=event.artist,
        event=event,
        song_request=item if kind == Transaction.Type.SONG_REQUEST else None,
        tip=item if kind == Transaction.Type.TIP else None,
        transaction_type=kind,
        amount=amount,
        phone_number=data["phone_number"],
    )
    try:
        result = initiate_stk_push(transaction)
    except PaymentError as exc:
        transaction.mark_failed(str(exc))
        messages.error(request, "M-Pesa could not be started. Check the number and try again.")
        return None
    transaction.merchant_request_id = result["MerchantRequestID"]
    transaction.checkout_request_id = result["CheckoutRequestID"]
    transaction.provider_response = result
    transaction.save(
        update_fields=["merchant_request_id", "checkout_request_id", "provider_response", "updated_at"]
    )
    return transaction


@ratelimit(key="ip", rate="20/h", method="POST", block=True)
def create_song_request(request, public_id):
    event = get_object_or_404(Event.objects.select_related("artist"), public_id=public_id)
    form = SongRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        transaction = _create_payment(request, event, form, kind=Transaction.Type.SONG_REQUEST)
        if transaction:
            return redirect("payments:status", public_id=transaction.public_id)
    return render(request, "music_requests/song_form.html", {"event": event, "form": form})


@ratelimit(key="ip", rate="20/h", method="POST", block=True)
def create_tip(request, public_id):
    event = get_object_or_404(Event.objects.select_related("artist"), public_id=public_id)
    form = TipForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        transaction = _create_payment(request, event, form, kind=Transaction.Type.TIP)
        if transaction:
            return redirect("payments:status", public_id=transaction.public_id)
    return render(request, "music_requests/tip_form.html", {"event": event, "form": form})


@login_required
def request_list(request):
    requests = (
        SongRequest.objects.filter(artist=request.user, status__in=[
            SongRequest.Status.PENDING,
            SongRequest.Status.ACCEPTED,
            SongRequest.Status.PLAYING,
            SongRequest.Status.PLAYED,
            SongRequest.Status.REJECTED,
        ])
        .select_related("event")
    )
    return render(request, "music_requests/list.html", {"song_requests": requests})


@login_required
@require_POST
def update_request_status(request, public_id):
    song_request = get_object_or_404(
        SongRequest, public_id=public_id, artist=request.user, status__in=[
            SongRequest.Status.PENDING,
            SongRequest.Status.ACCEPTED,
            SongRequest.Status.PLAYING,
        ]
    )
    transitions = {
        SongRequest.Status.PENDING: {
            "accept": SongRequest.Status.ACCEPTED,
            "reject": SongRequest.Status.REJECTED,
        },
        SongRequest.Status.ACCEPTED: {"playing": SongRequest.Status.PLAYING},
        SongRequest.Status.PLAYING: {"played": SongRequest.Status.PLAYED},
    }
    new_status = transitions.get(song_request.status, {}).get(request.POST.get("action"))
    if new_status is None:
        messages.error(request, "That status change is not allowed.")
    else:
        song_request.status = new_status
        song_request.save(update_fields=["status", "updated_at"])
        messages.success(request, f"Request marked {song_request.get_status_display().lower()}.")
    return redirect("music_requests:list")


@login_required
def request_feed(request):
    rows = SongRequest.objects.filter(
        artist=request.user, status=SongRequest.Status.PENDING
    ).values("public_id", "song_title", "song_artist", "requester_name", "amount", "tip_amount", "created_at")
    return JsonResponse(
        {
            "requests": [
                {
                    **row,
                    "public_id": str(row["public_id"]),
                    "created_at": row["created_at"].isoformat(),
                }
                for row in rows[:50]
            ]
        }
    )

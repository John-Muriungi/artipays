from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils import timezone

from events.models import Event
from music_requests.models import SongRequest, Tip
from payments.models import Transaction


@login_required
def home(request):
    artist = request.user
    successful = Transaction.objects.filter(artist=artist, status=Transaction.Status.SUCCESS)
    today = timezone.localdate()
    week_start = today - timedelta(days=6)
    daily = (
        successful.filter(created_at__date__gte=week_start)
        .values("created_at__date")
        .annotate(total=Sum("amount"))
        .order_by("created_at__date")
    )
    tip_earnings = successful.filter(transaction_type=Transaction.Type.TIP).aggregate(
        total=Sum("amount")
    )["total"] or 0
    song_tips = successful.filter(
        transaction_type=Transaction.Type.SONG_REQUEST
    ).aggregate(total=Sum("song_request__tip_amount"))["total"] or 0
    context = {
        "total_events": Event.objects.filter(artist=artist).count(),
        "active_events": Event.objects.filter(artist=artist, status=Event.Status.ACTIVE).count(),
        "total_requests": SongRequest.objects.filter(artist=artist, status__in=[
            SongRequest.Status.PENDING, SongRequest.Status.ACCEPTED,
            SongRequest.Status.PLAYING, SongRequest.Status.PLAYED, SongRequest.Status.REJECTED,
        ]).count(),
        "pending_requests": SongRequest.objects.filter(artist=artist, status=SongRequest.Status.PENDING).count(),
        "completed_requests": SongRequest.objects.filter(artist=artist, status=SongRequest.Status.PLAYED).count(),
        "earnings": successful.aggregate(total=Sum("amount"))["total"] or 0,
        "tip_earnings": tip_earnings + song_tips,
        "pending_payments": Transaction.objects.filter(artist=artist, status=Transaction.Status.PENDING).count(),
        "recent_requests": SongRequest.objects.filter(
            artist=artist, status=SongRequest.Status.PENDING
        ).select_related("event")[:5],
        "daily_earnings": list(daily),
    }
    return render(request, "dashboard/home.html", context)


@login_required
def earnings(request):
    transactions = Transaction.objects.filter(artist=request.user)
    today = timezone.localdate()
    period = request.GET.get("period", "all")
    if period == "today":
        transactions = transactions.filter(created_at__date=today)
    elif period == "7d":
        transactions = transactions.filter(created_at__date__gte=today - timedelta(days=6))
    elif period == "month":
        transactions = transactions.filter(created_at__year=today.year, created_at__month=today.month)
    elif period == "custom":
        start, end = request.GET.get("start"), request.GET.get("end")
        if start:
            transactions = transactions.filter(created_at__date__gte=start)
        if end:
            transactions = transactions.filter(created_at__date__lte=end)
    successful = transactions.filter(status=Transaction.Status.SUCCESS)
    song_transactions = successful.filter(transaction_type=Transaction.Type.SONG_REQUEST)
    tip_transactions = successful.filter(transaction_type=Transaction.Type.TIP)
    totals = successful.aggregate(
        gross=Sum("amount"),
    )
    song_revenue = song_transactions.aggregate(
        total=Sum(F("amount") - F("song_request__tip_amount"))
    )["total"] or 0
    tip_revenue = (
        tip_transactions.aggregate(total=Sum("amount"))["total"] or 0
    ) + (song_transactions.aggregate(total=Sum("song_request__tip_amount"))["total"] or 0)
    context = {
        "transactions": transactions.select_related("event").order_by("-created_at")[:200],
        "period": period,
        "gross": totals["gross"] or 0,
        "song_revenue": song_revenue,
        "tip_revenue": tip_revenue,
        "successful_count": successful.count(),
        "pending_count": transactions.filter(status=Transaction.Status.PENDING).count(),
        "failed_count": transactions.filter(status=Transaction.Status.FAILED).count(),
    }
    return render(request, "dashboard/earnings.html", context)

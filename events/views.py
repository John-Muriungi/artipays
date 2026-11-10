from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import EventForm
from .models import Event
from .qr import render_event_qr


@login_required
def event_list(request):
    events = Event.objects.filter(artist=request.user)
    return render(request, "events/list.html", {"events": events})


@login_required
def event_create(request):
    form = EventForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        event = form.save(commit=False)
        event.artist = request.user
        event.save()
        messages.success(request, "Event created. Its public QR code is ready.")
        return redirect("events:detail", pk=event.pk)
    return render(request, "events/form.html", {"form": form, "title": "Create event"})


@login_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk, artist=request.user)
    form = EventForm(request.POST or None, instance=event)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Event updated.")
        return redirect("events:detail", pk=event.pk)
    return render(request, "events/form.html", {"form": form, "title": "Edit event"})


@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, artist=request.user)
    return render(
        request,
        "events/detail.html",
        {"event": event, "public_url": request.build_absolute_uri(event.get_absolute_url())},
    )


@login_required
@require_POST
def event_set_status(request, pk):
    event = get_object_or_404(Event, pk=pk, artist=request.user)
    status = request.POST.get("status")
    if status not in Event.Status.values:
        raise Http404("Unknown event status.")
    event.status = status
    event.save(update_fields=["status", "updated_at"])
    messages.success(request, f"Event status changed to {event.get_status_display()}.")
    return redirect("events:detail", pk=event.pk)


def public_event(request, public_id):
    event = get_object_or_404(
        Event.objects.select_related("artist", "artist__artistprofile"), public_id=public_id
    )
    return render(request, "events/public.html", {"event": event})


@login_required
def event_qr(request, pk):
    event = get_object_or_404(Event, pk=pk, artist=request.user)
    if request.GET.get("download") == "1":
        return render_event_qr(event, download=True)
    return render(
        request,
        "events/qr_print.html",
        {"event": event, "qr_url": reverse("events:qr_image", kwargs={"pk": event.pk})},
    )


@login_required
def event_qr_image(request, pk):
    event = get_object_or_404(Event, pk=pk, artist=request.user)
    return render_event_qr(event)

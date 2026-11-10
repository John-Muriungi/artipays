import uuid

from django.conf import settings
from django.db import models

from events.models import Event


class SongRequest(models.Model):
    class Status(models.TextChoices):
        AWAITING_PAYMENT = "AWAITING_PAYMENT", "Awaiting payment"
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        PLAYING = "PLAYING", "Playing"
        PLAYED = "PLAYED", "Played"
        REJECTED = "REJECTED", "Rejected"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name="song_requests")
    artist = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="song_requests"
    )
    requester_name = models.CharField(max_length=80, blank=True)
    song_title = models.CharField(max_length=150)
    song_artist = models.CharField(max_length=150)
    message = models.CharField(max_length=300, blank=True)
    amount = models.PositiveIntegerField()
    tip_amount = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AWAITING_PAYMENT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("artist", "status", "created_at"))]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="song_request_amount_positive"),
            models.CheckConstraint(condition=models.Q(tip_amount__gte=0), name="song_request_tip_nonnegative"),
        ]

    def __str__(self):
        return f"{self.song_title} — {self.song_artist}"


class Tip(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name="tips")
    artist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tips")
    requester_name = models.CharField(max_length=80, blank=True)
    amount = models.PositiveIntegerField()
    message = models.CharField(max_length=300, blank=True)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("artist", "created_at"))]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="tip_amount_positive"),
        ]

    def __str__(self):
        return f"Tip KES {self.amount}"

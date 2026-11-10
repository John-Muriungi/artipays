import uuid

from django.conf import settings
from django.db import models

from events.models import Event
from music_requests.models import SongRequest, Tip


class Transaction(models.Model):
    class Type(models.TextChoices):
        SONG_REQUEST = "SONG_REQUEST", "Song request"
        TIP = "TIP", "Tip"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    artist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name="transactions")
    song_request = models.OneToOneField(
        SongRequest, null=True, blank=True, on_delete=models.PROTECT, related_name="transaction"
    )
    tip = models.OneToOneField(Tip, null=True, blank=True, on_delete=models.PROTECT, related_name="transaction")
    transaction_type = models.CharField(max_length=20, choices=Type.choices)
    amount = models.PositiveIntegerField(help_text="KES, whole shillings")
    currency = models.CharField(max_length=3, default="KES")
    phone_number = models.CharField(max_length=12)
    provider = models.CharField(max_length=20, default="MPESA")
    merchant_request_id = models.CharField(max_length=100, blank=True)
    checkout_request_id = models.CharField(max_length=100, blank=True, unique=True, null=True)
    provider_receipt = models.CharField(max_length=40, blank=True, unique=True, null=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    result_code = models.CharField(max_length=12, blank=True)
    result_description = models.CharField(max_length=255, blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    callback_data = models.JSONField(default=dict, blank=True)
    verification_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("artist", "status", "created_at"))]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="transaction_amount_positive"),
            models.CheckConstraint(
                condition=(
                    models.Q(transaction_type="SONG_REQUEST", song_request__isnull=False, tip__isnull=True)
                    | models.Q(transaction_type="TIP", tip__isnull=False, song_request__isnull=True)
                ),
                name="transaction_has_matching_item",
            ),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.public_id} ({self.status})"

    def mark_failed(self, detail):
        if self.status != self.Status.PENDING:
            return
        self.status = self.Status.FAILED
        self.result_description = str(detail)[:255]
        self.save(update_fields=["status", "result_description", "updated_at"])

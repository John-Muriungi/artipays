import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    artist = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="events"
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    venue = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=150, blank=True)
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    song_request_price = models.PositiveIntegerField(help_text="KES, whole shillings")
    minimum_tip = models.PositiveIntegerField(default=0, help_text="KES, whole shillings")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-event_date", "-start_time")
        indexes = [models.Index(fields=("artist", "status"))]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(song_request_price__gt=0),
                name="event_request_price_positive",
            )
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("events:public", kwargs={"public_id": self.public_id})

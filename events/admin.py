from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "artist", "event_date", "status", "song_request_price")
    list_filter = ("status", "event_date")
    search_fields = ("name", "venue", "artist__email")
    readonly_fields = ("public_id", "created_at", "updated_at")

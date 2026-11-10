from django.contrib import admin

from .models import SongRequest, Tip


@admin.register(SongRequest)
class SongRequestAdmin(admin.ModelAdmin):
    list_display = ("song_title", "song_artist", "artist", "event", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("song_title", "song_artist", "requester_name", "artist__email")


@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = ("artist", "event", "requester_name", "amount", "paid", "created_at")
    list_filter = ("paid", "created_at")
    search_fields = ("artist__email", "requester_name")

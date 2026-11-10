from django.contrib import admin

from .models import ArtistProfile


@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    list_display = ("stage_name", "user", "phone", "created_at")
    search_fields = ("stage_name", "user__email", "phone")

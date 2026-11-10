from django.conf import settings
from django.db import models


class ArtistProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stage_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=16)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to="artist_profiles/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.stage_name

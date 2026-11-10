from django.urls import path

from music_requests.consumers import ArtistRequestConsumer

websocket_urlpatterns = [
    path("ws/artist/requests/", ArtistRequestConsumer.as_asgi()),
]

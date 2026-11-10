from django.urls import path

from . import views

app_name = "music_requests"
urlpatterns = [
    path("event/<uuid:public_id>/request/", views.create_song_request, name="create"),
    path("event/<uuid:public_id>/tip/", views.create_tip, name="tip"),
    path("requests/", views.request_list, name="list"),
    path("requests/feed/", views.request_feed, name="feed"),
    path("requests/<uuid:public_id>/status/", views.update_request_status, name="status"),
]

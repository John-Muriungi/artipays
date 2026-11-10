from django.urls import path

from . import views

app_name = "events"
urlpatterns = [
    path("events/", views.event_list, name="list"),
    path("events/new/", views.event_create, name="create"),
    path("events/<int:pk>/", views.event_detail, name="detail"),
    path("events/<int:pk>/edit/", views.event_edit, name="edit"),
    path("events/<int:pk>/status/", views.event_set_status, name="status"),
    path("events/<int:pk>/qr/", views.event_qr, name="qr"),
    path("events/<int:pk>/qr.png", views.event_qr_image, name="qr_image"),
    path("event/<uuid:public_id>/", views.public_event, name="public"),
]

from django.urls import path

from . import views

app_name = "payments"
urlpatterns = [
    path("mpesa/callback/", views.mpesa_callback, name="callback"),
    path("<uuid:public_id>/", views.payment_status, name="status"),
    path("<uuid:public_id>/status.json", views.payment_status_json, name="status_json"),
    path("<uuid:public_id>/confirmation/", views.payment_confirmation, name="confirmation"),
]

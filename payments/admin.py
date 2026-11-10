from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("public_id", "artist", "event", "transaction_type", "amount", "status", "provider_receipt", "created_at")
    list_filter = ("status", "transaction_type", "provider", "created_at")
    search_fields = ("public_id", "artist__email", "event__name", "provider_receipt", "phone_number")
    readonly_fields = (
        "public_id", "provider_response", "callback_data", "verification_data",
        "created_at", "updated_at",
    )

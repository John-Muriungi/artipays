from urllib.parse import urlparse

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from payments.services import PaymentError, _access_token


class Command(BaseCommand):
    help = "Check Daraja sandbox credentials and public callback reachability."

    def handle(self, *args, **options):
        if settings.MPESA_ENVIRONMENT != "sandbox":
            raise CommandError("This check is restricted to MPESA_ENVIRONMENT=sandbox.")

        callback = urlparse(settings.MPESA_CALLBACK_URL)
        if callback.scheme != "https" or not callback.netloc:
            raise CommandError("MPESA_CALLBACK_URL must be a publicly reachable HTTPS URL.")

        try:
            _access_token()
        except PaymentError as exc:
            raise CommandError(f"Daraja sandbox authentication failed: {exc}") from exc

        try:
            response = requests.get(
                settings.MPESA_CALLBACK_URL,
                timeout=settings.MPESA_TIMEOUT_SECONDS,
                allow_redirects=False,
            )
        except requests.RequestException as exc:
            raise CommandError("Could not reach the configured callback URL.") from exc

        if response.status_code != 405:
            raise CommandError(
                "Callback URL did not reach the POST-only Django callback endpoint "
                f"(expected HTTP 405 to GET, received HTTP {response.status_code})."
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Daraja sandbox authentication passed; the public callback endpoint is reachable."
            )
        )

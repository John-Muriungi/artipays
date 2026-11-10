from io import BytesIO

import qrcode
from django.conf import settings
from django.http import HttpResponse


def render_event_qr(event, *, download=False):
    image = qrcode.make(f"{settings.SITE_URL}{event.get_absolute_url()}")
    output = BytesIO()
    image.save(output, format="PNG")
    response = HttpResponse(output.getvalue(), content_type="image/png")
    if download:
        response["Content-Disposition"] = f'attachment; filename="event-{event.public_id}.png"'
    return response

# Artipay

Artipay is a Django application for Kenyan DJs and musicians to accept paid song requests and tips for individual live events. It provides artist accounts, event-specific KES pricing, printable event QR codes, an audience checkout experience, an M-Pesa Daraja STK Push integration, and an earnings/request dashboard.

## What is included

- Artist registration, login/logout, profile updates, password change and email reset.
- Private artist dashboard, event CRUD/status control, earnings and transaction history.
- Public event pages addressed by a UUID and a generated QR code/print layout.
- Anonymous song requests and tips, with amounts determined and validated on the server.
- M-Pesa STK Push initiation, callback processing, server-side STK query verification, transaction idempotency, and public payment status/confirmation pages.
- Artist request queue with authenticated WebSocket notifications and HTTP polling fallback.
- Django admin, relational database constraints, responsive UI, basic unit/integration tests.

## Technology and layout

- Python 3.10+
- Django 5.1+
- PostgreSQL (SQLite is configured as a zero-setup local fallback)
- Daraja API, `qrcode` / Pillow, Daphne, Django Channels, Redis

```text
config/          Django settings, root URLs, WSGI, ASGI and WebSocket routing
accounts/        Artist profile, registration, authentication and profile forms
events/          Event management, public pages and QR generation
music_requests/  Song requests, tips and artist request queue
payments/        Transaction records, Daraja client and callback verification
dashboard/       Artist statistics and earnings views
templates/       Responsive artist and audience templates
static/          CSS and JavaScript (WebSocket updates with polling fallback)
```

## Local setup

1. Install Python 3.10 or later and PostgreSQL (or use SQLite for local development).
2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env`. Set a long random `SECRET_KEY`. For the SQLite fallback, remove `DATABASE_URL`; for PostgreSQL, create a database and set `DATABASE_URL`, for example:

   ```text
   DATABASE_URL=postgresql://artipay:your-password@localhost:5432/artipay
   ```

5. Apply database migrations and create the platform admin:

   ```powershell
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. Start the development server:

   ```powershell
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000/register/`. Registration intentionally does not sign the artist in; it redirects to `/login/`. Password reset email is written to the local console by default.

## Events and QR codes

Artists create events from the dashboard and choose an event-specific song-request price and minimum tip in whole KES. Each event has a randomly generated UUID public identifier. The QR page encodes `SITE_URL` plus the event public URL; it can render as a poster, download as PNG, or be printed from the browser. Set `SITE_URL` to the externally reachable HTTPS base URL in production.

Only events in `ACTIVE` status accept a new payment. Public event details remain available if an event is later closed.

## M-Pesa / Daraja configuration

Artipay initiates a Daraja STK Push. The audience browser never supplies the request price and never marks a payment successful. A callback is associated with the saved `CheckoutRequestID`, then the server queries Daraja's STK query endpoint and checks its result plus the expected amount, phone, and receipt before marking the transaction successful and revealing the request. Duplicate callbacks are idempotent. A failed/cancelled request is not visible to the artist.

Set these environment variables from the Safaricom Daraja app/business account:

```text
MPESA_ENVIRONMENT=sandbox              # use production only with approved production credentials
MPESA_CONSUMER_KEY=
MPESA_CONSUMER_SECRET=
MPESA_SHORTCODE=
MPESA_PASSKEY=
MPESA_CALLBACK_URL=https://your-domain/payments/mpesa/callback/
MPESA_TRANSACTION_TYPE=CustomerPayBillOnline
MPESA_TIMEOUT_SECONDS=20
```

The callback URL must be publicly reachable over HTTPS. Use the Daraja sandbox plus a secure tunnel during local integration tests. Run `python manage.py check_mpesa_sandbox` to verify that the credentials can obtain a sandbox access token and that the callback endpoint is reachable. This check does not initiate a payment. The end-to-end handset/simulator runbook is in [docs/PRODUCTION_DEPLOYMENT_CHECKLIST.md](./docs/PRODUCTION_DEPLOYMENT_CHECKLIST.md#daraja-sandbox-callback-test).

Safaricom credentials and live payment flows are not included or asserted as live-tested. If provider credentials are missing, the application reports payment initiation as failed and does not expose the request.

The callback endpoint is CSRF-exempt because Daraja cannot submit a browser CSRF token. It does not trust callback success on its own: the server-side STK query response is required before success is recorded. No client-supplied status or amount is trusted.

## Run tests and checks

```powershell
python manage.py test
python manage.py check
python manage.py check --deploy
```

The payment tests mock Daraja calls and test price authority, callback verification/idempotency, and unpaid-request privacy. WebSocket tests cover artist-only authenticated connections and notification delivery. A real M-Pesa sandbox account plus a publicly reachable HTTPS callback is needed to validate actual sandbox payment prompts and network callback delivery.

## Production deployment

The included `render.yaml` provisions a Render web service and PostgreSQL database; the ASGI application is served with Daphne for WebSockets. Use the provider-specific [production deployment checklist](./docs/PRODUCTION_DEPLOYMENT_CHECKLIST.md) for Render, AWS, or DigitalOcean. Before production:

1. Configure a unique secret key, database URL, a shared Redis-compatible `REDIS_URL`, public HTTPS `SITE_URL`, correct allowed hosts and CSRF trusted origins. `DEBUG=False` requires Redis for shared rate limiting.
2. Populate approved **production** Daraja credentials and an HTTPS callback URL in the hosting secret manager, never in source control.
3. Configure SMTP credentials for password-reset email (`EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`).
4. Run migrations, collect static files, and configure persistent media storage for artist profile images.
5. Enable HTTPS at the proxy/load balancer. Secure cookies, HSTS, SSL redirect, frame protections, and content-type protections are enabled when `DEBUG=False`.
6. Configure shared caching/rate limiting at the edge and monitor application/provider logs. Back up PostgreSQL and restrict admin access.

For Render, connect this repository and apply `render.yaml`; set `REDIS_URL`, `SITE_URL` and all M-Pesa variables in the dashboard. Redis is shared by rate limiting and Channels. Daphne serves both HTTP and WebSocket traffic in the same ASGI process; a separate Channels worker is not needed.

## Important operational notes

- Amounts use whole-shilling integer fields; there are no floating-point money calculations.
- Song requests and tips are created before checkout as pending records, but are only credited to artist-facing pages after verified payment.
- Payment status URLs use unguessable UUID identifiers and reveal only the associated payment's public status/confirmation.
- Artists' event, request, profile, transaction and earnings queries are scoped to the authenticated artist.
- Audience checkout POSTs are rate-limited per IP to 20 submissions per hour. Local development uses a process-local cache; production requires a shared Redis-compatible cache, and should monitor Daraja rate limits and callback delivery.
# artipays

# Production Deployment Checklist

This checklist assumes the Django application is deployed with Daphne, PostgreSQL, Redis, and an HTTPS reverse proxy. The ASGI entry point serves ordinary HTTP requests and authenticated artist WebSockets from the same process. Redis backs both Channels and Django's shared cache/rate limits.

## Before any production rollout

- [ ] Set `DEBUG=False` and provide a unique, strong `SECRET_KEY` through the provider's secret manager.
- [ ] Set `DATABASE_URL` to managed PostgreSQL. Restrict network access to the application.
- [ ] Set `REDIS_URL` to a private, managed Redis endpoint with TLS/authentication as required by the provider.
- [ ] Set `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and `SITE_URL` to the production hostnames.
- [ ] Set `SECURE_SSL_REDIRECT=True`; terminate TLS at the platform proxy and preserve `X-Forwarded-Proto`.
- [ ] Configure media storage with durable object storage. The default local media directory is not durable across ephemeral instances.
- [ ] Configure SMTP and test password-reset delivery.
- [ ] Apply migrations as a release/one-off step, then run `collectstatic --noinput`.
- [ ] Confirm health checks, structured logs, error reporting, database backups, and a rollback procedure.
- [ ] Use approved production Daraja credentials only after sandbox acceptance. Store them as secrets.
- [ ] Set `MPESA_CALLBACK_URL` to the exact public HTTPS callback path and register/allow it with the provider.
- [ ] Verify the load balancer/proxy allows WebSocket upgrades. Test both `wss://<host>/ws/artist/requests/` and HTTP polling fallback.
- [ ] Confirm production uses Daphne or another ASGI server; a WSGI-only Gunicorn process will not serve WebSockets.
- [ ] Run `python manage.py check --deploy` and the automated tests against the release build.

## Render

- [ ] Create a Render PostgreSQL database and a private Redis instance/add-on.
- [ ] Create the web service from this repository and use the included `render.yaml`.
- [ ] Confirm the service start command runs `daphne -b 0.0.0.0 -p $PORT config.asgi:application`.
- [ ] Configure `REDIS_URL`, `SITE_URL`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and email settings in the Render environment.
- [ ] Configure each `MPESA_*` variable as a secret/environment value; keep `MPESA_ENVIRONMENT=sandbox` until sandbox sign-off.
- [ ] Confirm the Render hostname is the callback URL host and the callback endpoint responds to HTTPS POSTs.
- [ ] Configure persistent/object storage for uploaded profile images; do not rely on the service filesystem.
- [ ] Check deploy logs for successful migrations/static collection and test dashboard WebSockets after deploy.

## AWS

Suggested managed topology: ECS/Fargate (or App Runner with WebSocket support validated), Application Load Balancer, RDS PostgreSQL, ElastiCache Redis, and S3 for media/static assets.

- [ ] Build and publish an immutable application container; run Daphne as the container command.
- [ ] Set the ALB idle timeout to support persistent WebSocket connections and confirm HTTP/1.1 WebSocket upgrade forwarding.
- [ ] Place ECS tasks, RDS, and Redis in private subnets; expose only the ALB publicly.
- [ ] Configure security groups so tasks can reach RDS and Redis, and only the ALB can reach task ports.
- [ ] Use Secrets Manager or Parameter Store for Django and Daraja secrets; grant the task role least-privilege access.
- [ ] Configure RDS backups, encryption, connection limits, and a migration/release task before traffic rollout.
- [ ] Configure ElastiCache TLS/authentication and set `REDIS_URL` accordingly.
- [ ] Configure S3 media storage with private buckets, least-privilege task role access, and lifecycle/backup policy.
- [ ] Configure ACM certificate, Route 53 DNS, ALB health checks, and `CSRF_TRUSTED_ORIGINS`.
- [ ] Send application logs to CloudWatch and configure alarms for 5xx errors, task restarts, DB capacity, and Redis availability.
- [ ] Verify WebSocket idle behavior, scale-out across multiple tasks, and Redis-backed group notifications.

## DigitalOcean

Deploy on App Platform only after confirming its current plan supports the required WebSocket upgrade behavior, or use a Droplet with a managed load balancer.

- [ ] Provision managed PostgreSQL and managed Redis; keep both private where supported.
- [ ] Deploy the ASGI app with Daphne (for example, `daphne -b 0.0.0.0 -p $PORT config.asgi:application` on App Platform).
- [ ] Configure build, release migration, and run commands separately; don't run migrations concurrently in every web worker.
- [ ] Configure secrets and runtime variables in App Platform, including `REDIS_URL`, allowed hosts, HTTPS origins, and Daraja credentials.
- [ ] Configure Spaces/object storage for media instead of local ephemeral disk.
- [ ] Configure the custom domain and TLS certificate, and verify forwarded HTTPS headers and WebSocket upgrades.
- [ ] For a Droplet deployment, place Nginx in front of Daphne and pass `Upgrade`/`Connection` headers for WebSockets.
- [ ] Configure firewall rules, automated backups, monitoring/alerts, log retention, and a documented rollback.
- [ ] Validate that all app replicas share Redis and can deliver a request notification to an artist connected to another replica.

## Daraja sandbox callback test

This is an end-to-end sandbox procedure. It requires a Daraja developer app/business configuration and does not use real production payments. The command below only checks authentication and callback reachability; it does not make a charge.

1. Create/configure a Daraja sandbox app with the STK Push product, and obtain the sandbox consumer key/secret, shortcode, and passkey from the provider.
2. Set `MPESA_ENVIRONMENT=sandbox`, `MPESA_CONSUMER_KEY`, `MPESA_CONSUMER_SECRET`, `MPESA_SHORTCODE`, `MPESA_PASSKEY`, and `MPESA_TRANSACTION_TYPE` in `.env` or the deployment secret manager.
3. Run the app locally with `python manage.py runserver`. Expose the local service using a trusted HTTPS tunnel. Do not publish Django admin or keep the tunnel open beyond the test.
4. Set `MPESA_CALLBACK_URL` to `<public-https-tunnel>/payments/mpesa/callback/` (including the trailing slash). This exact URL must route to the callback view.
5. Run `python manage.py check_mpesa_sandbox`. A pass confirms that sandbox OAuth works and a GET to the callback returns the expected `405 Method Not Allowed`; it is not evidence of a completed payment.
6. Create an artist and an active test event with a low test request price. Open the public event URL in a separate browser and submit a song request using a sandbox test MSISDN supported by the Daraja portal.
7. Complete or cancel the sandbox STK prompt/simulator flow. Confirm the provider sends its callback to the tunnel and that the application logs show callback processing. Do not manually mark a transaction paid.
8. For a completed payment, verify the payment status page becomes successful and the request becomes visible to the owning artist only after server-side STK query verification. For cancellation/failure, verify the request remains hidden.
9. Check WebSocket updates while the artist dashboard is open. With Redis configured, the paid request should appear without refreshing; when Redis/WebSockets are unavailable, polling should still update the request queue.
10. Run `python manage.py test payments music_requests` to verify automated callback idempotency, failed/unverified payment behavior, and authenticated WebSocket delivery. These tests mock Daraja and are separate from the live sandbox procedure.
11. Remove the tunnel and sandbox credentials when finished. Do not switch `MPESA_ENVIRONMENT` to `production` until Safaricom production approval and operational sign-off are complete.

Record the test date, sandbox app/environment, callback host (not credentials), transaction outcome, and application version. Never include consumer secrets, passkeys, access tokens, phone numbers, or callback payload PII in deployment notes.

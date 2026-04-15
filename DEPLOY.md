# Smart Grievance System Deployment Guide

This project supports three runtime profiles:

- Local development (`SQLite`, optional demo email mode)
- Public demo deployment (`PostgreSQL`, demo email mode)
- Production deployment (`PostgreSQL`, real SMTP email mode)

## 1. Required Runtime Configuration

Set these variables in your hosting environment.

| Variable | Required | Example |
|---|---|---|
| `FLASK_ENV` | Yes | `production` |
| `SECRET_KEY` | Yes | random 32+ char string |
| `APP_BASE_URL` | Yes | `https://your-domain.com` |
| `DATABASE_URL` | Yes | `postgresql://user:pass@host:5432/db` |
| `DEMO_EMAIL_MODE` | Yes | `true` for demo, `false` for real SMTP |
| `DEMO_SMS_MODE` | Yes | `true` (SMS is demo-only currently) |
| `AUTO_CREATE_TABLES` | Yes | `false` |

If `DEMO_EMAIL_MODE=false`, also set:

- `MAIL_SERVER`
- `MAIL_PORT`
- `MAIL_USE_TLS`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_DEFAULT_SENDER`

## 2. Render Deployment (Blueprint Recommended)

This repo includes `render.yaml` with:

- Python web service
- health check path (`/health`)
- managed PostgreSQL service binding for `DATABASE_URL`
- production-safe defaults (`AUTO_CREATE_TABLES=false`, scheduler autostart off)

### Steps

1. Open Render Dashboard → **New** → **Blueprint**.
2. Connect this GitHub repository.
3. Fill missing `sync: false` values (for example `APP_BASE_URL`, SMTP credentials).
4. Deploy.

## 3. Render Deployment (Manual Service Setup)

Use these values:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn "backend.app:create_app()" --bind 0.0.0.0:$PORT`
- Runtime: Python 3.11
- Health check path: `/health`

Attach a PostgreSQL database and map its connection string to `DATABASE_URL`.

## 4. Migrations and Seed Data

Run after first deployment (Render shell or release command):

```bash
python -m flask --app backend.app:create_app db upgrade
python manage.py seed
```

`manage.py seed` runs migrations first, then loads demo accounts/data.

## 5. Scheduler and Background Jobs

The app includes background tasks for comment escalation and scheduled retraining.

- Keep `ENABLE_SCHEDULER=true` unless intentionally disabling all background jobs.
- Keep `SCHEDULER_AUTOSTART=false` on normal web instances.
- Set `SCHEDULER_AUTOSTART=true` on exactly one dedicated instance/process only.

This prevents duplicate escalation/retraining runs across multiple web workers.

## 6. Health Endpoint

`GET /health` now returns:

- app status (`healthy` or `degraded`)
- environment and configured base URL
- DB connectivity details
- ML model loaded state
- scheduler runtime state

Status code behavior:

- `200`: app is up and DB is reachable
- `503`: DB connectivity check failed

## 7. Local Development Profile

Suggested local values:

```env
FLASK_ENV=development
SECRET_KEY=local-dev-secret
APP_BASE_URL=http://localhost:8000
DATABASE_URL=sqlite:///grievance.db
DEMO_EMAIL_MODE=true
DEMO_SMS_MODE=true
AUTO_CREATE_TABLES=false
```

Run locally:

```bash
pip install -r requirements.txt -r requirements-dev.txt
python -m flask --app backend.app:create_app db upgrade
python manage.py seed
python run.py
```

## 8. Static Demo (GitHub Pages)

`docs/` is a static showcase only. It does not use backend auth, DB, ML runtime, or real workflows.

Use it only for UI demonstration, not production or integration testing.

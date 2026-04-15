# Smart Grievance Redressal System

A citizen-centric grievance management platform for filing, tracking, and resolving complaints. Built for government departments with AI-powered department classification, role-based access, and automated workflows.

> **For security auditors:** The **full app** (Flask + `frontend/`) uses a server-side database, JWT auth, and server-side validation. The `docs/` folder is a **static demo only** (localStorage, no backend). See [SECURITY.md](SECURITY.md).

## Two Modes

| Mode | Path | Description |
|------|------|--------------|
| **Full app** | `frontend/` + Flask backend | Real database, JWT auth, ML classification. Run with `python run.py`. |
| **Static demo** | `docs/` | localStorage-only demo for GitHub Pages. No backend, no real auth. |

## Features

- **AI Department Classification** — ML model currently trains around ~74% accuracy on the bundled dataset and now uses confidence-aware routing
- **Confidence-Aware Triage** — High-confidence predictions auto-assign to departments; low-confidence predictions are routed to manual admin triage
- **Role-Based Access** — Citizens, Officers, and Admins with appropriate permissions
- **Fraud Detection** — Content moderation, spam blocking, duplicate detection
- **Comment & Escalation** — Officer-citizen communication with automatic escalation
- **Multi-Language Support** — Indian language stop words for better classification
- **Scheduled Retraining** — Model retrains weekly (configurable), supports manual retrain, and avoids overlapping retrain jobs
- **Public Transparency Feed** — Anonymized recently resolved cases exposed via backend API

## Role Model and Permissions

The active workflow model is intentionally simple and enforced server-side:

- `CITIZEN`
- `OFFICER`
- `ADMIN`

Legacy hierarchy fields (`role_level`, `current_role_level`, `RoleHierarchy`, `DepartmentMapping`) are retained for backward compatibility with older data/migrations, but they are no longer used for runtime authorization decisions.

### Permissions Matrix

| Action | Citizen | Officer | Admin |
|--------|---------|---------|-------|
| Submit grievance | Yes (own account only) | No | No |
| View grievance details | Own grievances only | Grievances in own department | All grievances |
| Update grievance status | No | Department grievances; cannot update cases assigned to another officer | All grievances |
| Add grievance comment | Own grievances only | Department grievances; cannot comment on cases assigned to another officer. First officer comment can claim unassigned case | All grievances |
| Assign officer | No | No | Yes (officer department must match grievance department, except manual-triage queue cases) |
| Report fraud | No | Assigned officer only | Review/take action |
| Export grievances | No | Own department only | All grievances |

### Escalation Rules

- Citizen comments start a 24-hour response window for the notified/assigned officer.
- On SLA miss, escalation target is resolved in this order:
  1. Assigned officer (if different from the originally notified officer)
  2. Another officer in the same department
  3. Admin fallback
- Every escalation writes an `EscalationLog` record (`auto` or `manual`).

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/smart-grievance-system.git
cd smart-grievance-system

pip install -r requirements.txt
python -m flask --app backend.app:create_app db upgrade
python manage.py seed
python run.py
```

Open **http://localhost:8000**

### Demo Accounts

| Role    | Email                     | Password   |
|---------|---------------------------|------------|
| Admin   | admin@grievance.gov       | admin123   |
| Officer | electricity@grievance.gov | officer123 |
| Citizen | citizen@example.com      | citizen123 |

## Project Structure

```
├── backend/           # Flask API
│   ├── routes/        # Auth, grievances, admin
│   ├── services/      # Classifier, email, scheduler
│   └── models.py      # Database models
├── migrations/        # Alembic revisions (Flask-Migrate)
├── frontend/          # Web UI (served by Flask)
│   ├── js/pages/      # Page-specific logic modules
│   ├── css/           # Page-level stylesheets
│   └── app.js         # Shared API/session helpers
├── ml/                # Training pipeline
│   ├── train.py       # Train classifier
│   └── artifacts/     # Saved model & vectorizer
├── data/              # Training dataset
├── manage.py          # Project CLI (seed command)
└── docs/              # Static demo (GitHub Pages)
```

## Database Setup (Local/Dev/Prod)

- **Dev default:** SQLite via `DATABASE_URL=sqlite:///grievance.db`
- **Prod:** PostgreSQL via `DATABASE_URL=postgresql://...`
- **Schema changes:** Managed through Flask-Migrate revisions in `migrations/`

### Migration workflow

```bash
# Create a new migration after model changes
python -m flask --app backend.app:create_app db migrate -m "describe change"

# Apply migrations
python -m flask --app backend.app:create_app db upgrade
```

### Seed workflow

```bash
# Applies pending migrations and seeds demo users
python manage.py seed
```

## API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | Login |
| `/api/auth/refresh-token` | POST | Exchange refresh token for new access token |
| `/api/auth/register` | POST | Register citizen |
| `/api/grievances/submit` | POST | Submit complaint |
| `/api/grievances/predict-department` | POST | AI department prediction |
| `/api/public/resolved-cases` | GET | Anonymized recent resolved grievances for homepage cards |
| `/api/admin/retrain-model` | POST | Trigger model retraining (Admin) |
| `/api/admin/model-status` | GET | Runtime + training metadata + correction-loop summary (Admin) |
| `/health` | GET | Health check |

## ML Routing Configuration

- `ML_AUTO_ASSIGN_CONFIDENCE_THRESHOLD` (default `0.65`) controls when auto-assignment is allowed.
- `ML_MANUAL_REVIEW_DEPARTMENT` (default `Manual Review Queue`) is the placeholder department for low-confidence cases.
- `ENABLE_SCHEDULED_RETRAIN` toggles scheduler-based retraining without disabling comment escalation.

When model confidence is below threshold, grievances are queued for manual triage and department corrections are logged for future retraining analysis.

## Deployment

### Render (Recommended)

1. Connect GitHub repo to [Render](https://render.com)
2. New Web Service → Python
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn "backend.app:create_app()" --bind 0.0.0.0:$PORT`
5. Add env: `FLASK_ENV=production`, `SECRET_KEY`, `DATABASE_URL`, `DEMO_EMAIL_MODE=true`
6. Run migrations: `python -m flask --app backend.app:create_app db upgrade`

See [DEPLOY.md](DEPLOY.md) for details. For auto-deploy on push to Render, add `.github/workflows/deploy.yml` via the GitHub web UI and set `RENDER_DEPLOY_HOOK_URL` in repo Secrets.

### GitHub Pages (Static Demo)

The `docs/` folder is a **static demo only** — it uses localStorage, has no backend, and does not reflect the production app. Enable in repo Settings → Pages → Source: branch `main`, folder `/docs`.

## Tech Stack

- **Backend:** Flask, SQLAlchemy, JWT
- **ML:** scikit-learn, TF-IDF, Logistic Regression
- **Frontend:** Vanilla JS, HTML5, CSS3

## Security

- **Auth:** Access JWT + password-reset JWT (+ optional refresh token) with explicit token types and expiries
- **Session model:** Tokens currently stored in browser `localStorage` (see `SECURITY.md` for tradeoff and HttpOnly-cookie migration note)
- **Lockout:** 3 failed logins = 24-hour server-side lockout per email
- **Rate limiting:** IP-based limits on login, registration, grievance submission
- **Validation:** Server-side for all inputs; bleach sanitization for XSS

## License

MIT

# Smart Grievance Redressal System

A citizen-centric grievance management platform for filing, tracking, and resolving complaints. Built for government departments with AI-powered department classification, role-based access, and automated workflows.

> **For security auditors:** The **full app** (Flask + `frontend/`) uses a server-side database, JWT auth, and server-side validation. The `docs/` folder is a **static demo only** (localStorage, no backend). See [SECURITY.md](SECURITY.md).

## Two Modes

| Mode | Path | Description |
|------|------|--------------|
| **Full app** | `frontend/` + Flask backend | Real database, JWT auth, ML classification. Run with `python run.py`. |
| **Static demo** | `docs/` | localStorage-only demo for GitHub Pages. No backend, no real auth. |

## Features

- **AI Department Classification** — ML model (~74% accuracy) routes complaints to the right department (Water, Electricity, Roads, Sanitation, etc.)
- **Role-Based Access** — Citizens, Officers, and Admins with appropriate permissions
- **Fraud Detection** — Content moderation, spam blocking, duplicate detection
- **Comment & Escalation** — Officer-citizen communication with automatic escalation
- **Multi-Language Support** — Indian language stop words for better classification
- **Scheduled Retraining** — Model retrains weekly; admins can trigger manually

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
| `/api/admin/retrain-model` | POST | Trigger model retraining (Admin) |
| `/api/admin/model-status` | GET | Model metadata (Admin) |
| `/health` | GET | Health check |

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

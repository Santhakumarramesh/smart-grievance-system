# Smart Grievance Redressal System
[![CI](https://github.com/Santhakumarramesh/smart-grievance-system/actions/workflows/ci.yml/badge.svg)](https://github.com/Santhakumarramesh/smart-grievance-system/actions/workflows/ci.yml)

A role-based grievance management platform for citizens, officers, and admins with ML-assisted department routing, fraud review workflows, and escalation-aware communication.

## What This Repo Contains

| Mode | Path | Purpose |
|---|---|---|
| Full application | `backend/` + `frontend/` | Real Flask API, database, JWT auth, ML routing, notifications |
| GitHub Pages mirror | `docs/` | Mirror of `frontend/` with runtime API base resolution for hosted static access |

`docs/` now uses the same UI code as `frontend/`, but API behavior still depends on reachable backend configuration.

## Architecture

High-level runtime flow:

```mermaid
graph LR
    U[Citizen / Officer / Admin] --> F[Frontend (Vanilla JS pages)]
    F -->|JWT + JSON API| A[Flask Application]
    A --> R[Auth + Role Guards + Validation]
    A --> G[Grievance Workflows]
    A --> N[Email + In-app Notifications]
    A --> M[ML Classifier + Metadata]
    A --> D[(SQLite / PostgreSQL)]
    S[Background Scheduler] --> G
    S --> M
```

Component summary:

- **Backend:** Flask app factory (`backend/app.py`) with route blueprints for auth, grievances, admin, and public/add-on APIs.
- **Frontend:** Vanilla JS role pages in `frontend/`, with shared API/session helpers in `frontend/app.js` and page modules in `frontend/js/pages/`.
- **ML pipeline:** scikit-learn model + vectorizer artifacts under `ml/artifacts/`, with confidence-aware routing and retrain support.
- **Auth:** JWT-based access/refresh/password-reset token flow with token types and server-side role guards.
- **Notifications:** Centralized email helper service plus persisted in-app notifications for workflow events.
- **Database:** SQLAlchemy models with Flask-Migrate/Alembic revisions; SQLite (dev) and PostgreSQL (prod).

Detailed architecture sections: [ARCHITECTURE.md](ARCHITECTURE.md)

## Core Workflows

1. Citizen submits complaint with location and optional/required image evidence (department-dependent).
2. Backend predicts department with ML confidence scoring.
3. High-confidence complaints auto-route; low-confidence complaints go to manual triage queue.
4. Admin assigns officer and manages triage/fraud actions.
5. Officer updates status, comments, and can report suspected fraud.
6. Notifications and escalation logic track overdue citizen comments.

## Current Scope (Implemented)

- Citizen grievance submission, tracking, and timeline updates.
- Officer dashboard flows: assigned grievances, updates, comments, fraud report submission.
- Admin flows: officer management, assignment, analytics, model status/retrain, fraud actions.
- JWT token architecture with explicit token types (`access`, `refresh`, `password_reset`).
- Password reset with OTP verification + reset token flow.
- ML-assisted department prediction with confidence-aware manual triage fallback.
- Real public stats and anonymized resolved-cases feed from backend.
- In-app + email notification helpers for core lifecycle events.
- Background scheduler for escalation checks and optional scheduled retraining.

## Current Scope (Known Limits)

- Frontend session tokens are stored in `localStorage` (documented tradeoff in `SECURITY.md`).
- UI language support is partially complete: selector is real, but translation coverage is not exhaustive across every page element.
- `content_moderator.py` exists, but full end-to-end moderation enforcement is not yet integrated into grievance submission logic.

## Setup Guide

Use the dedicated setup document:
- [SETUP.md](SETUP.md)

Quick local start:

```bash
git clone https://github.com/Santhakumarramesh/smart-grievance-system.git
cd smart-grievance-system

pip install -r requirements.txt -r requirements-dev.txt
python -m flask --app backend.app:create_app db upgrade
python manage.py seed
python run.py
```

Open [http://localhost:8000](http://localhost:8000)

Demo accounts created by seed:

| Role | Email | Password |
|---|---|---|
| Admin | `admin@grievance.gov` | `admin123` |
| Officer | `electricity@grievance.gov` | `officer123` |
| Citizen | `citizen@example.com` | `citizen123` |

## API Summary

- Full endpoint map: [API_SUMMARY.md](API_SUMMARY.md)
- Health endpoint: `GET /health` (app, DB, model, scheduler diagnostics)

## Database and Migrations

- Local default: `DATABASE_URL=sqlite:///grievance.db`
- Production target: PostgreSQL (`DATABASE_URL=postgresql://...`)
- Migration command:

```bash
python -m flask --app backend.app:create_app db migrate -m "describe change"
python -m flask --app backend.app:create_app db upgrade
```

## Quality Gates

CI (`.github/workflows/ci.yml`) runs:

- `ruff check backend tests`
- `python -m pytest --cov=backend --cov-report=term-missing --cov-report=xml`
- `bandit -q -r backend -x backend/seed.py` (non-blocking informational scan)
- optional smoke harness (manual trigger): `python scripts/smoke_test.py`

Local checks:

```bash
ruff check backend tests
python -m pytest --cov=backend --cov-report=term-missing
python scripts/smoke_test.py
```

To run smoke in GitHub Actions, trigger `CI` via `workflow_dispatch` with `run_smoke=true`.

## Deployment

- Production deployment guide: [DEPLOY.md](DEPLOY.md)
- Render blueprint config: `render.yaml`
- Required production envs include: `FLASK_ENV`, `SECRET_KEY`, `APP_BASE_URL`, `DATABASE_URL`.

## Future Enhancements

- Complete end-to-end translation coverage for all role pages.
- Move from `localStorage` tokens to HttpOnly cookie sessions.
- Fully wire content moderation scoring into submission acceptance/rejection pipeline.
- Improve SQLAlchemy 2.x modernization (`Query.get` replacements) and timezone-aware datetime handling.
- Expand automated test coverage beyond current critical backend flows.

## Security Notes

- See [SECURITY.md](SECURITY.md) for threat model assumptions and operational recommendations.

## License

MIT

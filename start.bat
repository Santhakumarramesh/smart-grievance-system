@echo off
echo ============================================================
echo Starting Smart Grievance System
echo ============================================================

REM Check if dependencies are installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Check if ML model exists
if not exist "ml\artifacts\model.joblib" (
    echo Training ML model...
    python ml\train.py
)

REM Check if database exists
if not exist "instance\grievance.db" (
    echo Setting up database...
    python -m backend.seed
)

REM Start the application
echo.
echo ============================================================
echo Starting application...
echo Open: http://localhost:8000
echo ============================================================
echo.
echo Test Accounts:
echo    Admin: admin@grievance.gov / admin123
echo    Officer: electricity@grievance.gov / officer123
echo    Citizen: citizen@example.com / citizen123
echo.
echo Press CTRL+C to stop the server
echo ============================================================
echo.

set PORT=8000
set PYTHONPATH=.
python backend\app.py

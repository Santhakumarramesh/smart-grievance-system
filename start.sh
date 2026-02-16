#!/bin/bash

echo "============================================================"
echo "🚀 Starting Smart Grievance System"
echo "============================================================"

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if ML model exists
if [ ! -f "ml/artifacts/model.joblib" ]; then
    echo "🤖 Training ML model..."
    python ml/train.py
fi

# Check if database exists
if [ ! -f "instance/grievance.db" ]; then
    echo "🗄️  Setting up database..."
    python -m backend.seed
fi

# Start the application
echo ""
echo "============================================================"
echo "✅ Starting application..."
echo "🌐 Open: http://localhost:8000"
echo "============================================================"
echo ""
echo "📋 Test Accounts:"
echo "   Admin: admin@grievance.gov / admin123"
echo "   Officer: electricity@grievance.gov / officer123"
echo "   Citizen: citizen@example.com / citizen123"
echo ""
echo "Press CTRL+C to stop the server"
echo "============================================================"
echo ""

PORT=8000 PYTHONPATH=. python backend/app.py

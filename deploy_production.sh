#!/bin/bash

# Smart Grievance System - Production Deployment Script
# This script helps deploy the application in production mode

echo "========================================"
echo "Smart Grievance System"
echo "Production Deployment"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with production settings"
    exit 1
fi

# Check if FLASK_ENV is set to production
if ! grep -q "FLASK_ENV=production" .env; then
    echo "⚠️  Warning: FLASK_ENV not set to production in .env"
    echo "Add this line to .env: FLASK_ENV=production"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if Gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "📦 Installing Gunicorn..."
    pip install gunicorn
fi

# Create wsgi.py if it doesn't exist
if [ ! -f wsgi.py ]; then
    echo "📝 Creating wsgi.py..."
    cat > wsgi.py << 'EOF'
from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
EOF
fi

# Run database migration
echo "🗄️  Running database migration..."
python migrate_db.py

# Train ML model
echo "🤖 Training ML model..."
python ml/train.py

# Create backup directory
if [ ! -d backups ]; then
    echo "📁 Creating backups directory..."
    mkdir -p backups
fi

# Backup database
echo "💾 Backing up database..."
timestamp=$(date +%Y%m%d_%H%M%S)
cp backend/grievance_system.db backups/grievance_system_${timestamp}.db
echo "✅ Backup created: backups/grievance_system_${timestamp}.db"

# Start Gunicorn
echo ""
echo "========================================"
echo "🚀 Starting Production Server"
echo "========================================"
echo ""
echo "Server will run on: http://0.0.0.0:8000"
echo "Press Ctrl+C to stop"
echo ""

# Run with Gunicorn
# -w 4: 4 worker processes
# -b 0.0.0.0:8000: Bind to all interfaces on port 8000
# --access-logfile -: Log to stdout
# --error-logfile -: Log errors to stdout
# --timeout 120: 120 second timeout
gunicorn -w 4 -b 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile - \
    --timeout 120 \
    wsgi:app

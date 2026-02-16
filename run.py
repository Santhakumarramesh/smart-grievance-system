#!/usr/bin/env python3
"""
Smart Grievance System - Application Entry Point
"""

from backend.app import create_app

if __name__ == '__main__':
    app = create_app()
    
    print("\n" + "="*70)
    print("🚀 Smart Grievance System - Starting Server")
    print("="*70)
    print(f"📍 URL: http://localhost:8000")
    print(f"🔒 Security: Enabled")
    print(f"📧 Email Mode: {'Demo (Console)' if app.config['DEMO_EMAIL_MODE'] else 'Production (SMTP)'}")
    print("="*70 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        use_reloader=False  # Disable reloader to prevent double initialization
    )

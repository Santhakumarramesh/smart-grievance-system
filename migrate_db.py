#!/usr/bin/env python3
"""
Database Migration Script
Adds new profile fields to User model
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.extensions import db
from backend.models import User, Grievance, OTPRequest, GrievanceUpdate, GrievanceComment
from backend.config import Config

# Initialize Flask app
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    print("🔄 Updating database schema...")
    
    # SQLite doesn't support ALTER TABLE ADD COLUMN for all types
    # We need to use raw SQL for adding columns
    from sqlalchemy import text, inspect
    
    inspector = inspect(db.engine)
    
    # Check existing columns in users table
    existing_columns = [col['name'] for col in inspector.get_columns('users')]
    
    # New columns to add
    new_user_columns = {
        'office_number': 'VARCHAR(50)',
        'office_email': 'VARCHAR(120)',
        'office_location': 'VARCHAR(500)',
        'office_building': 'VARCHAR(200)',
        'designation': 'VARCHAR(100)',
        'profile_photo': 'TEXT',
        'address': 'VARCHAR(500)',
        'city': 'VARCHAR(100)',
        'state': 'VARCHAR(100)',
        'pincode': 'VARCHAR(10)',
        'residential_address': 'TEXT',
        'residential_city': 'VARCHAR(100)',
        'residential_state': 'VARCHAR(100)',
        'residential_pincode': 'VARCHAR(10)',
        'date_of_birth': 'VARCHAR(20)',
        'gender': 'VARCHAR(20)'
    }
    
    print("\n📋 Adding new columns to User table:")
    for col_name, col_type in new_user_columns.items():
        if col_name not in existing_columns:
            try:
                db.session.execute(text(f'ALTER TABLE users ADD COLUMN {col_name} {col_type}'))
                db.session.commit()
                print(f"  ✓ Added {col_name}")
            except Exception as e:
                print(f"  ⚠ {col_name} - {str(e)}")
        else:
            print(f"  ✓ {col_name} (already exists)")
    
    # Check grievances table
    grievance_columns = [col['name'] for col in inspector.get_columns('grievances')]
    
    new_grievance_columns = {
        'assigned_officer_id': 'INTEGER',
        'complainant_dob': 'VARCHAR(20)',
        'complainant_gender': 'VARCHAR(50)',
        'images': 'TEXT',
        'is_flagged': 'BOOLEAN DEFAULT 0',
        'moderation_score': 'INTEGER DEFAULT 0',
        'moderation_severity': 'VARCHAR(20)',
        'moderation_flags': 'TEXT'
    }
    
    print("\n📋 Adding new columns to Grievance table:")
    for col_name, col_type in new_grievance_columns.items():
        if col_name not in grievance_columns:
            try:
                db.session.execute(text(f'ALTER TABLE grievances ADD COLUMN {col_name} {col_type}'))
                db.session.commit()
                print(f"  ✓ Added {col_name}")
            except Exception as e:
                print(f"  ⚠ {col_name} - {str(e)}")
        else:
            print(f"  ✓ {col_name} (already exists)")
    
    print("\n✅ Database schema updated successfully!")
    print("\n✅ Migration complete!")

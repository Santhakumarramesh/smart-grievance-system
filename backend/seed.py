"""
Seed script to create initial admin user and sample officers
Run this after first setup: python -m backend.seed
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.models import User
from backend.extensions import db

def seed_database():
    """Create initial admin and sample officers"""
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("Seeding Database")
        print("="*60)
        
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@grievance.gov').first()
        
        if admin:
            print("✓ Admin user already exists")
        else:
            # Create admin
            admin = User(
                name='System Administrator',
                email='admin@grievance.gov',
                phone='9999999999',
                role='ADMIN',
                email_verified=True,
                phone_verified=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✓ Created admin user")
            print(f"  Email: admin@grievance.gov")
            print(f"  Password: admin123")
        
        # Create sample officers for different departments
        departments = [
            'Water Supply',
            'Electricity',
            'Sanitation & Solid Waste',
            'Sewerage & Drainage',
            'Roads & Potholes',
            'Streetlights',
            'Traffic',
            'Police',
            'Cyber Crime',
            'Public Health',
            'Food Safety',
            'Education',
            'Land & Revenue',
            'Ration Card / PDS',
            'RTO / Transport',
            'Telecom / Network',
            'Environment'
        ]
        
        for dept in departments:
            email = f"{dept.lower().replace(' ', '')}@grievance.gov"
            officer = User.query.filter_by(email=email).first()
            
            if officer:
                print(f"✓ Officer for {dept} already exists")
            else:
                officer = User(
                    name=f"{dept} Officer",
                    email=email,
                    phone=f"98765{departments.index(dept):05d}",
                    role='OFFICER',
                    department=dept,
                    email_verified=True,
                    phone_verified=True
                )
                officer.set_password('officer123')
                db.session.add(officer)
                print(f"✓ Created officer for {dept}")
                print(f"  Email: {email}")
                print(f"  Password: officer123")
        
        # Create a sample citizen
        citizen_email = 'citizen@example.com'
        citizen = User.query.filter_by(email=citizen_email).first()
        
        if citizen:
            print("✓ Sample citizen already exists")
        else:
            citizen = User(
                name='John Doe',
                email=citizen_email,
                phone='9876543210',
                role='CITIZEN',
                email_verified=True,
                phone_verified=True
            )
            citizen.set_password('citizen123')
            db.session.add(citizen)
            print("✓ Created sample citizen")
            print(f"  Email: {citizen_email}")
            print(f"  Password: citizen123")
        
        db.session.commit()
        
        print("\n" + "="*60)
        print("Seeding completed successfully!")
        print("="*60)
        print("\nLogin Credentials:")
        print("-"*60)
        print("ADMIN:")
        print("  Email: admin@grievance.gov")
        print("  Password: admin123")
        print("\nOFFICER (any department):")
        print("  Email: [department]@grievance.gov")
        print("  Password: officer123")
        print("  Example: electricity@grievance.gov")
        print("\nCITIZEN:")
        print("  Email: citizen@example.com")
        print("  Password: citizen123")
        print("="*60)

if __name__ == '__main__':
    seed_database()

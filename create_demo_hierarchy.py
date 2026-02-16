#!/usr/bin/env python3
"""
Create Demo Hierarchy for Electricity Department
This script creates a complete hierarchical structure for testing the grievance system.
"""

from backend.app import create_app
from backend.extensions import db
from backend.models import User
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_demo_users():
    app = create_app()
    
    with app.app_context():
        print("🔧 Creating Electricity Department Hierarchy Demo Users...\n")
        
        # Demo users data
        demo_users = [
            {
                'email': 'snathar1500@gmail.com',
                'password': 'password123',
                'name': 'Santhakumar Nathar',
                'phone': '9876543210',
                'role': 'CITIZEN',
                'role_level': 0,
                'department': None,
                'ward': 'Ward 5',
                'district': 'Chennai',
                'state': 'Tamil Nadu',
                'date_of_birth': '1990-01-01',
                'gender': 'Male',
                'residential_address': '123 Main Street',
                'residential_city': 'Chennai',
                'residential_state': 'Tamil Nadu',
                'residential_pincode': '600001'
            },
            {
                'email': 'lineman@electricity.gov.in',
                'password': 'password123',
                'name': 'Ravi Kumar',
                'phone': '9876543211',
                'role': 'OFFICER',
                'role_level': 1,  # Field Officer
                'department': 'Electricity',
                'ward': 'Ward 5',
                'district': 'Chennai',
                'state': 'Tamil Nadu',
                'jurisdiction_type': 'ward',
                'designation': 'Line Man',
                'office_number': '+91-44-2345-6701',
                'office_email': 'lineman@electricity.gov.in',
                'office_location': 'Ward 5 Electricity Office',
                'office_building': 'Ground Floor, Municipal Building',
                'date_of_birth': '1985-05-15',
                'gender': 'Male'
            },
            {
                'email': 'juniorengineer@electricity.gov.in',
                'password': 'password123',
                'name': 'Priya Sharma',
                'phone': '9876543212',
                'role': 'OFFICER',
                'role_level': 2,  # Section Officer / Manager
                'department': 'Electricity',
                'ward': None,
                'district': 'Chennai',
                'state': 'Tamil Nadu',
                'jurisdiction_type': 'district',
                'designation': 'Junior Engineer',
                'office_number': '+91-44-2345-6702',
                'office_email': 'juniorengineer@electricity.gov.in',
                'office_location': 'Chennai District Electricity Office',
                'office_building': '2nd Floor, District Office Complex',
                'date_of_birth': '1988-08-20',
                'gender': 'Female'
            },
            {
                'email': 'chiefengineer@electricity.gov.in',
                'password': 'password123',
                'name': 'Rajesh Patel',
                'phone': '9876543213',
                'role': 'OFFICER',
                'role_level': 3,  # Department Head
                'department': 'Electricity',
                'ward': None,
                'district': None,
                'state': 'Tamil Nadu',
                'jurisdiction_type': 'state',
                'designation': 'Chief Engineer',
                'office_number': '+91-44-2345-6703',
                'office_email': 'chiefengineer@electricity.gov.in',
                'office_location': 'Tamil Nadu Electricity Board Headquarters',
                'office_building': 'Executive Wing, 5th Floor',
                'date_of_birth': '1975-03-10',
                'gender': 'Male'
            },
            {
                'email': 'admin@example.com',
                'password': 'admin123',
                'name': 'System Administrator',
                'phone': '9876543214',
                'role': 'ADMIN',
                'role_level': 6,  # Admin
                'department': None,
                'ward': None,
                'district': None,
                'state': None,
                'jurisdiction_type': None,
                'designation': 'System Administrator',
                'office_number': '+91-44-2345-6700',
                'office_email': 'admin@example.com',
                'office_location': 'Central Administration',
                'office_building': 'Admin Block',
                'date_of_birth': '1980-01-01',
                'gender': 'Other'
            }
        ]
        
        created_users = []
        
        for user_data in demo_users:
            # Check if user already exists
            existing_user = User.query.filter_by(email=user_data['email']).first()
            
            if existing_user:
                print(f"⚠️  User {user_data['email']} already exists. Skipping...")
                created_users.append(existing_user)
                continue
            
            # Create new user
            user = User(
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                name=user_data['name'],
                phone=user_data['phone'],
                role=user_data['role'],
                role_level=user_data['role_level'],
                department=user_data.get('department'),
                ward=user_data.get('ward'),
                district=user_data.get('district'),
                jurisdiction_type=user_data.get('jurisdiction_type'),
                designation=user_data.get('designation'),
                office_number=user_data.get('office_number'),
                office_email=user_data.get('office_email'),
                office_location=user_data.get('office_location'),
                office_building=user_data.get('office_building'),
                date_of_birth=user_data.get('date_of_birth'),
                gender=user_data.get('gender'),
                residential_address=user_data.get('residential_address'),
                residential_city=user_data.get('residential_city'),
                residential_state=user_data.get('residential_state'),
                residential_pincode=user_data.get('residential_pincode'),
                email_verified=True,
                phone_verified=True
            )
            
            db.session.add(user)
            created_users.append(user)
            print(f"✅ Created: {user_data['email']} ({user_data.get('designation', 'Citizen')})")
        
        db.session.commit()
        
        print("\n" + "="*70)
        print("🎉 DEMO HIERARCHY CREATED SUCCESSFULLY!")
        print("="*70)
        print("\n📋 LOGIN CREDENTIALS:\n")
        
        print("👤 CITIZEN (Your Account):")
        print("   Email: snathar1500@gmail.com")
        print("   Password: password123")
        print("   Role: Can submit complaints\n")
        
        print("⚡ LINE MAN (Field Officer):")
        print("   Email: lineman@electricity.gov.in")
        print("   Password: password123")
        print("   Role: Resolves complaints in Ward 5\n")
        
        print("🔧 JUNIOR ENGINEER (Section Officer/Manager):")
        print("   Email: juniorengineer@electricity.gov.in")
        print("   Password: password123")
        print("   Role: Manages Chennai District, assigns to Line Man\n")
        
        print("👔 CHIEF ENGINEER (Department Head):")
        print("   Email: chiefengineer@electricity.gov.in")
        print("   Password: password123")
        print("   Role: Oversees entire Tamil Nadu Electricity\n")
        
        print("🛡️  ADMIN (System Administrator):")
        print("   Email: admin@example.com")
        print("   Password: admin123")
        print("   Role: Full system access\n")
        
        print("="*70)
        print("\n🔄 DEMO WORKFLOW:")
        print("1. Login as Citizen (snathar1500@gmail.com)")
        print("2. Submit an electricity complaint in Ward 5, Chennai")
        print("3. Login as Admin to assign to Junior Engineer")
        print("4. Login as Junior Engineer to assign to Line Man")
        print("5. Login as Line Man to resolve the complaint")
        print("6. Citizen receives updates at each step!")
        print("\n✨ The hierarchy is hidden from citizens - they only see status updates!\n")

if __name__ == '__main__':
    create_demo_users()

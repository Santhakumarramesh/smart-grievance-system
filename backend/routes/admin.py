from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func
from backend.models import User, Grievance, GrievanceUpdate
from backend.extensions import db
from backend.routes.auth import get_current_user_from_token

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/create-officer', methods=['POST'])
def create_officer():
    """
    Create a new officer account (Admin only)
    Required: name, email, phone, password, department
    """
    try:
        user = get_current_user_from_token()
        if not user or user.role != 'ADMIN':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'password', 'department']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create officer
        officer = User(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            role='OFFICER',
            department=data['department'],
            email_verified=True,  # Auto-verify officers
            phone_verified=True
        )
        officer.set_password(data['password'])
        
        db.session.add(officer)
        db.session.commit()
        
        return jsonify({
            'message': 'Officer created successfully',
            'officer': officer.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/officers', methods=['GET'])
def get_officers():
    """
    Get all officers (Admin only)
    """
    try:
        user = get_current_user_from_token()
        if not user or user.role != 'ADMIN':
            return jsonify({'error': 'Admin access required'}), 403
        
        officers = User.query.filter_by(role='OFFICER').all()
        
        return jsonify({
            'officers': [officer.to_dict() for officer in officers]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
def get_users():
    """
    Get all users/citizens (Admin only)
    """
    try:
        user = get_current_user_from_token()
        if not user or user.role != 'ADMIN':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get all citizens
        citizens = User.query.filter_by(role='CITIZEN').all()
        
        # Get grievance count for each citizen
        users_data = []
        for citizen in citizens:
            user_dict = citizen.to_dict()
            grievance_count = Grievance.query.filter_by(user_id=citizen.id).count()
            user_dict['grievance_count'] = grievance_count
            users_data.append(user_dict)
        
        return jsonify({
            'users': users_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/analytics', methods=['GET'])
def get_analytics():
    """
    Get system analytics (Admin only)
    Returns:
    - counts_by_status
    - counts_by_department
    - avg_resolution_time_days
    - total_grievances
    - total_users
    """
    try:
        user = get_current_user_from_token()
        if not user or user.role != 'ADMIN':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Count by status
        status_counts = db.session.query(
            Grievance.status,
            func.count(Grievance.id)
        ).group_by(Grievance.status).all()
        
        counts_by_status = {status: count for status, count in status_counts}
        
        # Count by department
        dept_counts = db.session.query(
            Grievance.assigned_department,
            func.count(Grievance.id)
        ).group_by(Grievance.assigned_department).all()
        
        counts_by_department = {dept: count for dept, count in dept_counts}
        
        # Calculate average resolution time for closed/resolved grievances
        resolved_grievances = Grievance.query.filter(
            Grievance.status.in_(['Resolved', 'Closed'])
        ).all()
        
        total_resolution_time = 0
        resolved_count = 0
        
        for grievance in resolved_grievances:
            if grievance.created_at and grievance.updated_at:
                resolution_time = (grievance.updated_at - grievance.created_at).total_seconds()
                total_resolution_time += resolution_time
                resolved_count += 1
        
        avg_resolution_time_days = 0
        if resolved_count > 0:
            avg_resolution_time_seconds = total_resolution_time / resolved_count
            avg_resolution_time_days = round(avg_resolution_time_seconds / (24 * 3600), 2)
        
        # Total counts
        total_grievances = Grievance.query.count()
        total_users = User.query.filter_by(role='CITIZEN').count()
        total_officers = User.query.filter_by(role='OFFICER').count()
        
        return jsonify({
            'counts_by_status': counts_by_status,
            'counts_by_department': counts_by_department,
            'avg_resolution_time_days': avg_resolution_time_days,
            'total_grievances': total_grievances,
            'total_users': total_users,
            'total_officers': total_officers
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/all-grievances', methods=['GET'])
def get_all_grievances():
    """
    Get all grievances with complete user and officer information (Admin only)
    """
    try:
        user = get_current_user_from_token()
        if not user or user.role != 'ADMIN':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get query parameters for filtering
        status = request.args.get('status')
        department = request.args.get('department')
        
        query = Grievance.query
        
        if status:
            query = query.filter_by(status=status)
        
        if department:
            query = query.filter_by(assigned_department=department)
        
        grievances = query.order_by(Grievance.created_at.desc()).all()
        
        # Build detailed grievance data with complete user and officer information
        grievances_data = []
        for g in grievances:
            grievance_dict = g.to_dict(include_officer=True)
            
            # Add complete complainant (user) information
            complainant = User.query.get(g.user_id)
            if complainant:
                grievance_dict['complainant'] = {
                    'id': complainant.id,
                    'name': complainant.name,
                    'email': complainant.email,
                    'phone': complainant.phone,
                    'residential_address': complainant.residential_address,
                    'residential_city': complainant.residential_city,
                    'residential_state': complainant.residential_state,
                    'residential_pincode': complainant.residential_pincode,
                    'date_of_birth': complainant.date_of_birth,
                    'gender': complainant.gender,
                    'email_verified': complainant.email_verified,
                    'phone_verified': complainant.phone_verified,
                    'created_at': complainant.created_at.isoformat() if complainant.created_at else None
                }
            
            grievances_data.append(grievance_dict)
        
        return jsonify({
            'grievances': grievances_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/departments', methods=['GET'])
def get_departments():
    """
    Get list of all departments
    """
    try:
        user = get_current_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Get unique departments from grievances and officers
        dept_from_grievances = db.session.query(Grievance.assigned_department).distinct().all()
        dept_from_officers = db.session.query(User.department).filter(User.role == 'OFFICER').distinct().all()
        
        departments = set()
        for (dept,) in dept_from_grievances:
            if dept:
                departments.add(dept)
        for (dept,) in dept_from_officers:
            if dept:
                departments.add(dept)
        
        return jsonify({
            'departments': sorted(list(departments))
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

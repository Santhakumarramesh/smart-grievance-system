from flask import Blueprint, request, jsonify
from datetime import datetime
from backend.models import Grievance, GrievanceUpdate, GrievanceComment, User
from backend.extensions import db
from backend.routes.auth import get_current_user_from_token
from backend.services.classifier import classifier
from backend.services.email_service import EmailService

grievances_bp = Blueprint('grievances', __name__)

# Departments that REQUIRE images (physical/infrastructure issues)
DEPARTMENTS_REQUIRING_IMAGES = {
    'Water Supply', 'Electricity', 'Sanitation & Solid Waste',
    'Sewerage & Drainage', 'Roads & Potholes', 'Streetlights',
    'Traffic', 'Public Health', 'Food Safety', 'Environment',
    'Telecom / Network'
}

# Departments where images are OPTIONAL (administrative/document issues)
DEPARTMENTS_OPTIONAL_IMAGES = {
    'Police', 'Cyber Crime', 'Education', 'Land & Revenue',
    'Ration Card / PDS', 'RTO / Transport'
}

def does_department_require_images(department):
    """Check if a department requires mandatory images"""
    return department in DEPARTMENTS_REQUIRING_IMAGES

@grievances_bp.route('/predict-department', methods=['POST'])
def predict_department():
    """
    Predict department for a complaint text (for dynamic UI updates)
    Required: complaint_text
    """
    try:
        user = get_current_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        complaint_text = data.get('complaint_text')
        
        if not complaint_text:
            return jsonify({'error': 'Complaint text is required'}), 400
        
        # Predict department
        predicted_department = classifier.predict(complaint_text)
        
        # Check if images are required
        images_required = does_department_require_images(predicted_department)
        
        return jsonify({
            'department': predicted_department,
            'images_required': images_required
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@grievances_bp.route('/submit', methods=['POST'])
def submit_grievance():
    """
    Submit a new grievance
    Required: complaint_text
    Optional: location
    """
    try:
        user = get_current_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        complaint_text = data.get('complaint_text')
        location = data.get('location', '')
        images = data.get('images', [])
        
        if not complaint_text or len(complaint_text.strip()) < 20:
            return jsonify({'error': 'Complaint text must be at least 20 characters'}), 400
        
        if not location or len(location.strip()) < 10:
            return jsonify({'error': 'Please provide a detailed location'}), 400
        
        # Predict department using ML first
        predicted_department = classifier.predict(complaint_text)
        
        # CONDITIONAL: Validate images based on department type
        images_required = does_department_require_images(predicted_department)
        
        if images_required and (not images or len(images) == 0):
            return jsonify({
                'error': f'At least 1 image is mandatory for {predicted_department} complaints. Visual evidence is required to verify and process this type of complaint.'
            }), 400
        
        if images and len(images) > 5:
            return jsonify({'error': 'Maximum 5 images allowed'}), 400
        
        # Get complainant info from user profile
        complainant_dob = user.date_of_birth
        complainant_gender = user.gender
        
        # Store images as JSON
        import json
        images_json = json.dumps(images) if images else None
        
        # Create grievance
        grievance = Grievance(
            user_id=user.id,
            complaint_text=complaint_text,
            predicted_department=predicted_department,
            assigned_department=predicted_department,
            status='Received',
            location=location,
            images=images_json,
            complainant_dob=complainant_dob,
            complainant_gender=complainant_gender
        )
        
        db.session.add(grievance)
        db.session.flush()  # Get the grievance ID
        
        # Create first update - Received
        update1 = GrievanceUpdate(
            grievance_id=grievance.id,
            status='Received',
            message='Your complaint has been received and is being processed.',
            updated_by_role='SYSTEM',
            updated_by_name='Smart Grievance System'
        )
        db.session.add(update1)
        
        # Create second update - Assigned to Department
        update2 = GrievanceUpdate(
            grievance_id=grievance.id,
            status='Assigned to Department',
            message=f'Your complaint has been assigned to {predicted_department} department for review.',
            updated_by_role='SYSTEM',
            updated_by_name='Smart Grievance System'
        )
        db.session.add(update2)
        
        # Update grievance status
        grievance.status = 'Assigned to Department'
        
        db.session.commit()
        
        # Send email notification
        EmailService.send_grievance_notification(
            user.email,
            grievance.id,
            predicted_department,
            'Assigned to Department',
            f'Your complaint has been assigned to {predicted_department} department.'
        )
        
        return jsonify({
            'message': 'Grievance submitted successfully',
            'grievance_id': grievance.id,
            'department': predicted_department,
            'status': grievance.status
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@grievances_bp.route('/my-grievances', methods=['GET'])
def get_my_grievances():
    """
    Get all grievances for current user
    """
    try:
        user = get_current_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        grievances = Grievance.query.filter_by(user_id=user.id).order_by(Grievance.created_at.desc()).all()
        
        return jsonify({
            'grievances': [g.to_dict() for g in grievances]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@grievances_bp.route('/<int:grievance_id>', methods=['GET'])
def get_grievance(grievance_id):
    """
    Get grievance details with timeline
    """
    try:
        user = get_current_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        grievance = Grievance.query.get(grievance_id)
        
        if not grievance:
            return jsonify({'error': 'Grievance not found'}), 404
        
        # Check authorization
        if user.role == 'CITIZEN' and grievance.user_id != user.id:
            return jsonify({'error': 'Unauthorized to view this grievance'}), 403
        
        if user.role == 'OFFICER' and grievance.assigned_department != user.department:
            return jsonify({'error': 'Unauthorized to view this grievance'}), 403
        
        return jsonify({
            'grievance': grievance.to_dict(include_updates=True, include_comments=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@grievances_bp.route('/department/<department>', methods=['GET'])
def get_department_grievances(department):
    """
    Get all grievances for a department (Officer only)
    """
    try:
        user = get_current_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        if user.role not in ['OFFICER', 'ADMIN']:
            return jsonify({'error': 'Only officers can access this endpoint'}), 403
        
        # Officers can only see their department
        if user.role == 'OFFICER' and user.department != department:
            return jsonify({'error': 'Unauthorized to view this department'}), 403
        
        grievances = Grievance.query.filter_by(
            assigned_department=department
        ).order_by(Grievance.created_at.desc()).all()
        
        return jsonify({
            'grievances': [g.to_dict() for g in grievances]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@grievances_bp.route('/<int:grievance_id>/update', methods=['POST'])
def update_grievance(grievance_id):
    """
    Update grievance status (Officer/Admin only)
    Required: status, message
    """
    try:
        user = get_current_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        if user.role not in ['OFFICER', 'ADMIN']:
            return jsonify({'error': 'Only officers can update grievances'}), 403
        
        data = request.get_json()
        new_status = data.get('status')
        message = data.get('message')
        
        if not new_status or not message:
            return jsonify({'error': 'status and message are required'}), 400
        
        # Valid statuses
        valid_statuses = [
            'Received',
            'Assigned to Department',
            'Under Progress',
            'Investigation',
            'Reviewed',
            'Resolved',
            'Closed'
        ]
        
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        
        grievance = Grievance.query.get(grievance_id)
        
        if not grievance:
            return jsonify({'error': 'Grievance not found'}), 404
        
        # Check authorization
        if user.role == 'OFFICER' and grievance.assigned_department != user.department:
            return jsonify({'error': 'Unauthorized to update this grievance'}), 403
        
        # Create update entry
        update = GrievanceUpdate(
            grievance_id=grievance.id,
            status=new_status,
            message=message,
            updated_by_role=user.role,
            updated_by_name=user.name
        )
        db.session.add(update)
        
        # Update grievance status
        grievance.status = new_status
        grievance.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Send email notification to citizen
        citizen = User.query.get(grievance.user_id)
        if citizen:
            EmailService.send_grievance_notification(
                citizen.email,
                grievance.id,
                grievance.assigned_department,
                new_status,
                message
            )
        
        return jsonify({
            'message': 'Grievance updated successfully',
            'grievance': grievance.to_dict(include_updates=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@grievances_bp.route('/<int:grievance_id>/comments', methods=['GET'])
def get_comments(grievance_id):
    """
    Get all comments for a grievance
    """
    try:
        user = get_current_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        grievance = Grievance.query.get(grievance_id)
        
        if not grievance:
            return jsonify({'error': 'Grievance not found'}), 404
        
        # Check authorization
        if user.role == 'CITIZEN' and grievance.user_id != user.id:
            return jsonify({'error': 'Unauthorized to view this grievance'}), 403
        
        if user.role == 'OFFICER' and grievance.assigned_department != user.department:
            return jsonify({'error': 'Unauthorized to view this grievance'}), 403
        
        comments = GrievanceComment.query.filter_by(
            grievance_id=grievance_id
        ).order_by(GrievanceComment.created_at.asc()).all()
        
        return jsonify({
            'comments': [comment.to_dict() for comment in comments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@grievances_bp.route('/<int:grievance_id>/comments', methods=['POST'])
def add_comment(grievance_id):
    """
    Add a comment to a grievance (Citizen or Officer)
    Required: comment_text
    """
    try:
        user = get_current_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        comment_text = data.get('comment_text')
        
        if not comment_text or len(comment_text.strip()) < 5:
            return jsonify({'error': 'Comment must be at least 5 characters'}), 400
        
        grievance = Grievance.query.get(grievance_id)
        
        if not grievance:
            return jsonify({'error': 'Grievance not found'}), 404
        
        # Check authorization
        if user.role == 'CITIZEN' and grievance.user_id != user.id:
            return jsonify({'error': 'Unauthorized to comment on this grievance'}), 403
        
        if user.role == 'OFFICER' and grievance.assigned_department != user.department:
            return jsonify({'error': 'Unauthorized to comment on this grievance'}), 403
        
        # Create comment
        comment = GrievanceComment(
            grievance_id=grievance_id,
            user_id=user.id,
            comment_text=comment_text,
            user_role=user.role,
            user_name=user.name
        )
        
        db.session.add(comment)
        db.session.commit()
        
        # Send email notification to the other party
        if user.role == 'CITIZEN':
            # Notify officers of the department
            officers = User.query.filter_by(
                role='OFFICER',
                department=grievance.assigned_department
            ).all()
            
            for officer in officers:
                EmailService.send_email(
                    officer.email,
                    f'New Comment on Grievance #{grievance_id}',
                    f"""
Dear {officer.name},

A citizen has added a new comment on Grievance #{grievance_id}:

"{comment_text}"

View and respond at: http://localhost:5000/track.html?id={grievance_id}

Best regards,
Smart Grievance System
                    """
                )
        else:
            # Notify citizen
            citizen = User.query.get(grievance.user_id)
            if citizen:
                EmailService.send_email(
                    citizen.email,
                    f'New Response on Your Grievance #{grievance_id}',
                    f"""
Dear {citizen.name},

{user.name} from {grievance.assigned_department} department has responded to your grievance:

"{comment_text}"

View and respond at: http://localhost:5000/track.html?id={grievance_id}

Best regards,
Smart Grievance System
                    """
                )
        
        return jsonify({
            'message': 'Comment added successfully',
            'comment': comment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

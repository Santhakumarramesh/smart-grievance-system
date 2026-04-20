from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
from backend.models import Grievance, GrievanceUpdate, GrievanceComment, User, FraudReport, RoleHierarchy
from backend.models_addons import AuditLog, GrievanceRating, DepartmentCorrectionLog
from backend.extensions import db
from backend.config import Config
from backend.routes.auth import get_current_user_from_token
from backend.services.classifier import classifier
from backend.services.email_service import EmailService
from backend.services.notification_service import NotificationService
from backend.services.ai_image_detector import AIImageDetector
from backend.services.comment_escalation import check_and_escalate_comments, escalate_comment_manually
from backend.services.content_moderator import ContentModerator
from backend.services.audit_service import log_audit
from backend.security import require_firewall, SecurityFirewall, SecurityLogger
from backend.utils.roles import ADMIN_ROLE_VALUES, OFFICER_ROLE_VALUES, canonical_role, is_role
from backend.utils.workflow import can_view_grievance, can_officer_act_on_grievance
from backend.utils.validation import (
    ValidationError,
    validate_comment_text,
    validate_complaint_text,
    validate_location,
    validate_update_message,
)

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
        user, auth_response = get_current_user_from_token(return_error=True)
        if auth_response:
            return auth_response

        data = request.get_json() or {}
        complaint_text = data.get('complaint_text')
        
        if not complaint_text:
            return jsonify({'error': 'Complaint text is required'}), 400

        is_valid, sanitized_text, error = SecurityFirewall.validate_input(complaint_text, 'complaint_text')
        if not is_valid:
            return jsonify({'error': error or 'Invalid complaint text'}), 400
        
        # Predict department with confidence metadata
        prediction = classifier.predict_with_confidence(sanitized_text)
        predicted_department = prediction['department']
        prediction_confidence = float(prediction.get('confidence') or 0.0)
        
        # Check if images are required
        images_required = does_department_require_images(predicted_department)
        requires_manual_review = (
            (not prediction.get('model_loaded'))
            or (prediction_confidence < Config.ML_AUTO_ASSIGN_CONFIDENCE_THRESHOLD)
        )
        
        return jsonify({
            'department': predicted_department,
            'images_required': images_required,
            'prediction_confidence': prediction_confidence,
            'prediction_confidence_pct': round(prediction_confidence * 100, 2),
            'top_candidates': prediction.get('top_candidates', []),
            'requires_manual_review': requires_manual_review,
            'routing_decision': 'manual_review' if requires_manual_review else 'auto_assign',
            'auto_assign_threshold': Config.ML_AUTO_ASSIGN_CONFIDENCE_THRESHOLD,
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@grievances_bp.route('/submit', methods=['POST'])
@require_firewall(max_requests=20, window_minutes=60)  # Max 20 grievances per hour
def submit_grievance():
    """
    Submit a new grievance
    Required: complaint_text
    Optional: location
    """
    try:
        user, auth_response = get_current_user_from_token(return_error=True, required_roles=['CITIZEN'])
        if auth_response:
            return auth_response

        data = request.get_json() or {}
        complaint_text = data.get('complaint_text')
        location = data.get('location', '')
        images = data.get('images', [])

        try:
            complaint_text = validate_complaint_text(complaint_text)
            location = validate_location(location)
        except ValidationError as validation_error:
            return jsonify({'error': str(validation_error)}), 400
        
        # ── Content Moderation ──
        moderation_result = ContentModerator.moderate_content(complaint_text)
        if ContentModerator.should_block_submission(moderation_result):
            return jsonify({
                'error': 'Inappropriate Content Violation',
                'message': ContentModerator.get_user_warning_message(moderation_result),
                'moderation': {
                    'severity': moderation_result['severity'],
                    'score': moderation_result['score'],
                },
            }), 400

        # Predict department using ML with confidence.
        prediction = classifier.predict_with_confidence(complaint_text)
        predicted_department = prediction['department']
        prediction_confidence = float(prediction.get('confidence') or 0.0)
        prediction_source = prediction.get('source', 'fallback')
        requires_manual_triage = (
            (not prediction.get('model_loaded'))
            or (prediction_confidence < Config.ML_AUTO_ASSIGN_CONFIDENCE_THRESHOLD)
        )
        
        # CONDITIONAL: Validate images based on department type
        images_required = does_department_require_images(predicted_department)
        
        if images_required and (not images or len(images) == 0):
            return jsonify({
                'error': f'At least 1 image is mandatory for {predicted_department} complaints. Visual evidence is required to verify and process this type of complaint.'
            }), 400
        
        if images and len(images) > 5:
            return jsonify({'error': 'Maximum 5 images allowed'}), 400
        
        # AI-GENERATED IMAGE DETECTION (Anti-Fraud Measure)
        ai_image_detected = False
        ai_detection_confidence = 0.0
        ai_detection_details = None
        
        if images and len(images) > 0:
            ai_detection_result = AIImageDetector.batch_detect(images)
            
            if ai_detection_result['ai_detected_count'] > 0:
                # AI-generated images detected
                ai_images = [r for r in ai_detection_result['results'] if r['is_ai_generated']]
                
                # Get highest confidence detection
                highest_confidence = max(ai_images, key=lambda x: x['confidence'])
                
                if highest_confidence['confidence'] >= 85:
                    # Very high confidence AI detection - REJECT with helpful message
                    return jsonify({
                        'error': 'AI-Generated Image Detected',
                        'message': f'Image #{highest_confidence["image_index"]} appears to be created by AI software (Confidence: {highest_confidence["confidence"]}%).\n\n'
                                   f'Reason: {highest_confidence["reasons"][0] if highest_confidence["reasons"] else "AI generation signatures found in image metadata"}\n\n'
                                   f'Please upload REAL PHOTOS taken with your phone or camera showing the actual issue. '
                                   f'Officers will visit the site to verify, so authentic photos are required.',
                        'image_index': highest_confidence['image_index'],
                        'confidence': highest_confidence['confidence'],
                        'ai_detection': True,
                        'action_required': 'Please remove the AI-generated image and upload a real photo of the complaint location.'
                    }), 400
                elif highest_confidence['confidence'] >= 60:
                    # Medium confidence - FLAG for officer verification
                    print(f"⚠️  FLAGGED: Possible AI-generated image in complaint (confidence: {highest_confidence['confidence']}%)")
                    ai_image_detected = True
                    ai_detection_confidence = highest_confidence['confidence']
                    ai_detection_details = json.dumps({
                        'image_index': highest_confidence['image_index'],
                        'confidence': highest_confidence['confidence'],
                        'reasons': highest_confidence['reasons'],
                        'warnings': highest_confidence['warnings'],
                        'note': 'Flagged for officer verification during site visit'
                    })
        
        # Get complainant info from user profile
        complainant_dob = user.date_of_birth
        complainant_gender = user.gender
        
        # Store images as JSON
        images_json = json.dumps(images) if images else None

        routing_status = 'Assigned to Department'
        assigned_department = predicted_department
        routing_message = f'Your complaint has been assigned to {predicted_department} department for review.'
        triage_reason = None

        if requires_manual_triage:
            routing_status = 'Manual Review Required'
            assigned_department = Config.ML_MANUAL_REVIEW_DEPARTMENT
            routing_message = (
                f'Your complaint has been routed to manual triage because model confidence '
                f'({prediction_confidence * 100:.1f}%) is below the auto-assign threshold '
                f'({Config.ML_AUTO_ASSIGN_CONFIDENCE_THRESHOLD * 100:.1f}%). '
                f'Admin review is pending.'
            )
            triage_reason = (
                f'Low model confidence ({prediction_confidence * 100:.1f}%) for '
                f'predicted department "{predicted_department}"'
            )
        
        # Determine moderation flags to store
        # Flag if not safe OR if severity is not none (e.g. medium/low still flagged for review)
        is_flagged = (not moderation_result['is_safe']) or (moderation_result['severity'].lower() not in ['safe', 'none'])
        moderation_score = moderation_result['score']
        moderation_severity = moderation_result['severity']
        moderation_flags_json = json.dumps(moderation_result['flags']) if moderation_result['flags'] else None

        # Compute SLA deadline
        now = datetime.utcnow()
        from sqlalchemy import func
        # Case-insensitive lookup for department config
        dept_config = RoleHierarchy.query.filter(func.lower(RoleHierarchy.department) == func.lower(assigned_department)).first()
        sla_hours = dept_config.sla_hours if dept_config and dept_config.sla_hours else 48
        sla_deadline = now + timedelta(hours=sla_hours)

        # Create grievance
        grievance = Grievance(
            user_id=user.id,
            complaint_text=complaint_text,
            predicted_department=predicted_department,
            assigned_department=assigned_department,
            prediction_confidence=prediction_confidence,
            prediction_source=prediction_source,
            requires_manual_triage=requires_manual_triage,
            triage_reason=triage_reason,
            status='Received',
            location=location,
            images=images_json,
            complainant_dob=complainant_dob,
            complainant_gender=complainant_gender,
            ai_image_detected=ai_image_detected,
            ai_detection_confidence=ai_detection_confidence,
            ai_detection_details=ai_detection_details,
            # Content moderation
            is_flagged=is_flagged,
            moderation_score=moderation_score,
            moderation_severity=moderation_severity,
            moderation_flags=moderation_flags_json,
            # SLA tracking
            sla_hours=sla_hours,
            sla_deadline=sla_deadline,
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
            status=routing_status,
            message=routing_message,
            updated_by_role='SYSTEM',
            updated_by_name='Smart Grievance System'
        )
        db.session.add(update2)
        
        # Update grievance status
        grievance.status = routing_status

        if requires_manual_triage:
            admins = User.query.filter(User.role.in_(ADMIN_ROLE_VALUES)).all()
            for admin in admins:
                NotificationService.queue_notification(
                    user_id=admin.id,
                    title=f'Manual ML Triage Needed - Grievance #{grievance.id}',
                    message=(
                        f'Predicted: {predicted_department} | '
                        f'Confidence: {prediction_confidence * 100:.1f}% | '
                        f'Citizen: {user.name}'
                    ),
                    notification_type='triage_review',
                    related_grievance_id=grievance.id,
                    is_read=False,
                )

        # Notify admins if content was flagged by moderation
        if is_flagged and ContentModerator.should_notify_admin(moderation_result):
            admins_for_moderation = User.query.filter(User.role.in_(ADMIN_ROLE_VALUES)).all()
            for admin in admins_for_moderation:
                NotificationService.queue_notification(
                    user_id=admin.id,
                    title=f'⚠️ Flagged Content - Grievance #{grievance.id}',
                    message=(
                        f'Content moderation flagged this complaint (severity: {moderation_severity}, '
                        f'score: {moderation_score}). Citizen: {user.name}'
                    ),
                    notification_type='content_moderation',
                    related_grievance_id=grievance.id,
                    is_read=False,
                )
        
        db.session.commit()
        
        # Send email notification
        EmailService.send_grievance_notification(
            user.email,
            grievance.id,
            predicted_department,
            routing_status,
            routing_message
        )
        
        log_audit(
            user.id,
            'create_grievance',
            'grievance',
            grievance.id,
            json.dumps({
                'department': predicted_department,
                'prediction_confidence': prediction_confidence,
                'routing_status': routing_status,
                'requires_manual_triage': requires_manual_triage,
                'moderation_score': moderation_score,
                'moderation_severity': moderation_severity,
                'is_flagged': is_flagged,
            })
        )
        
        response_data = {
            'message': 'Grievance submitted successfully',
            'grievance_id': grievance.id,
            'department': predicted_department,
            'status': grievance.status,
            'routing_decision': 'manual_review' if requires_manual_triage else 'auto_assign',
            'prediction_confidence': prediction_confidence,
            'auto_assign_threshold': Config.ML_AUTO_ASSIGN_CONFIDENCE_THRESHOLD,
            'sla_deadline': sla_deadline.isoformat(),
        }
        if is_flagged:
            response_data['content_warning'] = moderation_result['message']

        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@grievances_bp.route('/my-grievances', methods=['GET'])
def get_my_grievances():
    """
    Get all grievances for current user
    """
    try:
        user, auth_response = get_current_user_from_token(return_error=True)
        if auth_response:
            return auth_response
        
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
        user, auth_response = get_current_user_from_token(return_error=True)
        if auth_response:
            return auth_response
        
        grievance = Grievance.query.get(grievance_id)
        
        if not grievance:
            return jsonify({'error': 'Grievance not found'}), 404
        
        allowed, error = can_view_grievance(user, grievance)
        if not allowed:
            return jsonify({'error': error}), 403

        include_officer = canonical_role(user.role) in ['OFFICER', 'ADMIN']
        return jsonify({
            'grievance': grievance.to_dict(include_updates=True, include_comments=True, include_officer=include_officer)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@grievances_bp.route('/department/<department>', methods=['GET'])
def get_department_grievances(department):
    """
    Get all grievances for a department (Officer only)
    """
    try:
        user, auth_response = get_current_user_from_token(return_error=True, required_roles=['OFFICER', 'ADMIN'])
        if auth_response:
            return auth_response
        
        # Officers can only see their department
        if is_role(user, 'OFFICER') and user.department != department:
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
        user, auth_response = get_current_user_from_token(return_error=True, required_roles=['OFFICER', 'ADMIN'])
        if auth_response:
            return auth_response

        data = request.get_json() or {}
        new_status = data.get('status')
        message = data.get('message')
        
        if not new_status or not message:
            return jsonify({'error': 'status and message are required'}), 400

        try:
            message = validate_update_message(message)
        except ValidationError as validation_error:
            return jsonify({'error': str(validation_error)}), 400
        
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
        
        if is_role(user, 'OFFICER'):
            allowed, error = can_officer_act_on_grievance(user, grievance)
            if not allowed:
                return jsonify({'error': error}), 403
        
        # Store old status for notification
        old_status = grievance.status
        
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
        grievance.last_action_at = datetime.utcnow()

        # Clear SLA breach on terminal statuses (resolved/closed)
        if new_status in ('Resolved', 'Closed'):
            grievance.sla_breached = False

        # First officer action on an unassigned grievance claims ownership.
        if is_role(user, 'OFFICER') and not grievance.assigned_officer_id:
            grievance.assigned_officer_id = user.id
        
        # Assign officer if status is "Assigned to Department" and not already assigned
        if new_status == 'Assigned to Department' and not grievance.assigned_officer_id:
            grievance.assigned_officer_id = user.id
            
        # ── ML Correction Logging ──
        if 'assigned_department' in data and data['assigned_department'] != grievance.predicted_department:
            # Check if this correction was already logged to avoid duplicates
            existing_correction = DepartmentCorrectionLog.query.filter_by(
                grievance_id=grievance.id,
                corrected_department=data['assigned_department']
            ).first()
            
            if not existing_correction:
                correction = DepartmentCorrectionLog(
                    grievance_id=grievance.id,
                    predicted_department=grievance.predicted_department or "Unknown",
                    corrected_department=data['assigned_department'],
                    prediction_confidence=0.0, # Placeholder or fetch if stored
                    corrected_by_user_id=user.id,
                    reason=message or "Manual department correction"
                )
                db.session.add(correction)

        if 'assigned_department' in data:
            grievance.assigned_department = data['assigned_department']
        
        db.session.commit()
        
        # Send email notification to citizen with detailed update
        citizen = User.query.get(grievance.user_id)
        if citizen:
            EmailService.send_status_update_notification(
                user_email=citizen.email,
                user_name=citizen.name,
                grievance_id=grievance.id,
                old_status=old_status,
                new_status=new_status,
                update_message=message,
                department=grievance.assigned_department,
                officer_name=user.name
            )
        
        log_audit(user.id, 'update_grievance', 'grievance', grievance_id, json.dumps({'old_status': old_status, 'new_status': new_status}))
        
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
        user, auth_response = get_current_user_from_token(return_error=True)
        if auth_response:
            return auth_response
        
        grievance = Grievance.query.get(grievance_id)
        
        if not grievance:
            return jsonify({'error': 'Grievance not found'}), 404
        
        allowed, error = can_view_grievance(user, grievance)
        if not allowed:
            return jsonify({'error': error}), 403
        
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
        user, auth_response = get_current_user_from_token(return_error=True)
        if auth_response:
            return auth_response
        
        data = request.get_json() or {}
        comment_text = data.get('comment_text')
        try:
            comment_text = validate_comment_text(comment_text)
        except ValidationError as validation_error:
            return jsonify({'error': str(validation_error)}), 400
        
        grievance = Grievance.query.get(grievance_id)
        
        if not grievance:
            return jsonify({'error': 'Grievance not found'}), 404
        
        if is_role(user, 'CITIZEN'):
            if grievance.user_id != user.id:
                return jsonify({'error': 'Unauthorized to comment on this grievance'}), 403
        elif is_role(user, 'OFFICER'):
            allowed, error = can_officer_act_on_grievance(user, grievance)
            if not allowed:
                return jsonify({'error': error}), 403
            if not grievance.assigned_officer_id:
                grievance.assigned_officer_id = user.id
                grievance.updated_at = datetime.utcnow()
        
        # Create comment
        comment = GrievanceComment(
            grievance_id=grievance_id,
            user_id=user.id,
            comment_text=comment_text,
            user_role=user.role,
            user_name=user.name
        )
        
        db.session.add(comment)
        pending_email_jobs = []
        
        # Prepare notification recipients and escalation metadata before commit.
        if is_role(user, 'CITIZEN'):
            # Notify ONLY the currently assigned officer (not all officers)
            if grievance.assigned_officer_id:
                assigned_officer = User.query.get(grievance.assigned_officer_id)
                
                if assigned_officer:
                    # Track notification for escalation
                    comment.notified_officer_id = assigned_officer.id
                    comment.notification_sent_at = datetime.utcnow()
                    comment.response_deadline = datetime.utcnow() + timedelta(hours=24)  # 24 hours to respond

                    pending_email_jobs.append((
                        EmailService.send_citizen_comment_alert,
                        {
                            'officer_email': assigned_officer.email,
                            'officer_name': assigned_officer.name,
                            'grievance_id': grievance_id,
                            'comment_text': comment_text,
                            'response_hours': 24,
                        }
                    ))
                    
                    # Create in-app notification
                    NotificationService.queue_notification(
                        user_id=assigned_officer.id,
                        title=f'New Comment on Grievance #{grievance_id}',
                        message=f'Citizen has commented: "{comment_text[:100]}..." - Response required within 24 hours.',
                        notification_type='comment',
                        related_grievance_id=grievance_id,
                    )
            else:
                # If no specific officer assigned, notify department head
                dept_head = User.query.filter(
                    User.department == grievance.assigned_department,
                    User.role.in_(OFFICER_ROLE_VALUES)
                ).order_by(User.id.asc()).first()  # Get first officer as fallback
                
                if dept_head:
                    comment.notified_officer_id = dept_head.id
                    comment.notification_sent_at = datetime.utcnow()
                    comment.response_deadline = datetime.utcnow() + timedelta(hours=24)

                    pending_email_jobs.append((
                        EmailService.send_citizen_comment_alert,
                        {
                            'officer_email': dept_head.email,
                            'officer_name': dept_head.name,
                            'grievance_id': grievance_id,
                            'comment_text': comment_text,
                            'response_hours': 24,
                        }
                    ))
                    NotificationService.queue_notification(
                        user_id=dept_head.id,
                        title=f'New Comment on Grievance #{grievance_id}',
                        message=f'Citizen has commented: "{comment_text[:100]}..." - Response required within 24 hours.',
                        notification_type='comment',
                        related_grievance_id=grievance_id,
                    )
        else:
            # Notify citizen
            citizen = User.query.get(grievance.user_id)
            if citizen:
                pending_email_jobs.append((
                    EmailService.send_officer_reply_alert,
                    {
                        'citizen_email': citizen.email,
                        'citizen_name': citizen.name,
                        'grievance_id': grievance_id,
                        'officer_name': user.name,
                        'department': grievance.assigned_department,
                        'comment_text': comment_text,
                    }
                ))

        db.session.commit()

        for email_fn, kwargs in pending_email_jobs:
            try:
                email_fn(**kwargs)
            except Exception as email_error:
                print(f"Failed to send comment notification email: {email_error}")
        
        return jsonify({
            'message': 'Comment added successfully',
            'comment': comment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@grievances_bp.route('/<int:grievance_id>/report-fraud', methods=['POST'])
def report_fraud(grievance_id):
    """
    Report a grievance as fraudulent (Officer only)
    Officers can report complaints after site visit verification
    """
    try:
        user, auth_response = get_current_user_from_token(return_error=True, required_roles=['OFFICER'])
        if auth_response:
            return auth_response
        
        data = request.get_json()
        fraud_type = data.get('fraud_type')
        description = data.get('description')
        site_visit_notes = data.get('site_visit_notes', '')
        evidence = data.get('evidence', '')
        
        if not fraud_type or not description:
            return jsonify({'error': 'fraud_type and description are required'}), 400
        
        # Valid fraud types
        valid_fraud_types = [
            'false_complaint',
            'fake_images',
            'wrong_location',
            'exaggerated',
            'duplicate',
            'malicious'
        ]
        
        if fraud_type not in valid_fraud_types:
            return jsonify({'error': f'Invalid fraud_type. Must be one of: {", ".join(valid_fraud_types)}'}), 400
        
        grievance = Grievance.query.get(grievance_id)
        if not grievance:
            return jsonify({'error': 'Grievance not found'}), 404
        
        allowed, error = can_officer_act_on_grievance(user, grievance, require_assignment=True)
        if not allowed:
            return jsonify({'error': error}), 403
        
        # Check if already reported
        existing_report = FraudReport.query.filter_by(
            grievance_id=grievance_id,
            reported_by_officer_id=user.id
        ).first()
        
        if existing_report:
            return jsonify({'error': 'You have already reported this grievance as fraudulent'}), 400
        
        # Create fraud report
        fraud_report = FraudReport(
            grievance_id=grievance_id,
            reported_by_officer_id=user.id,
            complainant_user_id=grievance.user_id,
            fraud_type=fraud_type,
            description=description,
            site_visit_notes=site_visit_notes,
            evidence=evidence,
            status='Pending'
        )
        db.session.add(fraud_report)
        pending_email_jobs = []
        
        # Update grievance status
        grievance.status = 'Under Investigation - Fraud Reported'
        grievance.updated_at = datetime.utcnow()
        
        # Create update entry
        update = GrievanceUpdate(
            grievance_id=grievance_id,
            status='Under Investigation - Fraud Reported',
            message=f'Officer {user.name} has reported this complaint as potentially fraudulent after site visit. Admin review pending.',
            updated_by_role='OFFICER',
            updated_by_name=user.name
        )
        db.session.add(update)
        
        # Notify admin
        admins = User.query.filter(User.role.in_(ADMIN_ROLE_VALUES)).all()
        for admin in admins:
            NotificationService.queue_notification(
                user_id=admin.id,
                title=f'Fraud Report - Grievance #{grievance_id}',
                message=f'Officer {user.name} reported grievance #{grievance_id} as {fraud_type.replace("_", " ")}. Immediate review required.',
                notification_type='fraud_report',
                related_grievance_id=grievance_id,
                is_read=False,
            )
            pending_email_jobs.append((
                EmailService.send_fraud_report_alert,
                {
                    'admin_email': admin.email,
                    'admin_name': admin.name,
                    'grievance_id': grievance_id,
                    'officer_name': user.name,
                    'fraud_type': fraud_type.replace('_', ' '),
                    'description': description,
                }
            ))
        
        # Notify complainant (warning)
        complainant = User.query.get(grievance.user_id)
        if complainant:
            NotificationService.queue_notification(
                user_id=complainant.id,
                title=f'Complaint Under Review - Grievance #{grievance_id}',
                message=f'Your complaint is under investigation for verification. An officer visited the site and raised concerns. Admin will review and contact you if needed.',
                notification_type='fraud_warning',
                related_grievance_id=grievance_id,
                is_read=False,
            )
            pending_email_jobs.append((
                EmailService.send_fraud_review_notice,
                {
                    'citizen_email': complainant.email,
                    'citizen_name': complainant.name,
                    'grievance_id': grievance_id,
                    'stage': 'under_review',
                    'details': (
                        f'Officer {user.name} submitted a fraud review request for your complaint. '
                        'Admin verification is in progress.'
                    ),
                }
            ))
        
        db.session.commit()

        for email_fn, kwargs in pending_email_jobs:
            try:
                email_fn(**kwargs)
            except Exception as email_error:
                print(f"Failed to send fraud-report notification email: {email_error}")
        
        return jsonify({
            'message': 'Fraud report submitted successfully. Admin will review.',
            'fraud_report_id': fraud_report.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@grievances_bp.route('/fraud-reports', methods=['GET'])
def get_fraud_reports():
    """
    Get fraud reports (Admin only)
    """
    try:
        user, auth_response = get_current_user_from_token(return_error=True, required_roles=['ADMIN'])
        if auth_response:
            return auth_response
        
        reports = FraudReport.query.order_by(FraudReport.created_at.desc()).all()
        
        reports_data = []
        for report in reports:
            report_dict = report.to_dict()
            
            # Add officer details
            officer = User.query.get(report.reported_by_officer_id)
            if officer:
                report_dict['officer_name'] = officer.name
                report_dict['officer_department'] = officer.department
            
            # Add complainant details
            complainant = User.query.get(report.complainant_user_id)
            if complainant:
                report_dict['complainant_name'] = complainant.name
                report_dict['complainant_email'] = complainant.email
                report_dict['complainant_warnings'] = complainant.fraud_warnings
                report_dict['complainant_suspended'] = complainant.account_suspended
            
            # Add grievance details
            grievance = Grievance.query.get(report.grievance_id)
            if grievance:
                report_dict['grievance_text'] = grievance.complaint_text[:200]
                report_dict['grievance_department'] = grievance.assigned_department
            
            reports_data.append(report_dict)
        
        return jsonify({
            'fraud_reports': reports_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@grievances_bp.route('/fraud-reports/<int:report_id>/action', methods=['POST'])
def take_fraud_action(report_id):
    """
    Take action on fraud report (Admin only)
    """
    try:
        user, auth_response = get_current_user_from_token(return_error=True, required_roles=['ADMIN'])
        if auth_response:
            return auth_response
        
        data = request.get_json()
        action = data.get('action')  # 'verify', 'dismiss', 'warn', 'suspend'
        admin_notes = data.get('admin_notes', '')
        
        if not action:
            return jsonify({'error': 'action is required'}), 400
        
        report = FraudReport.query.get(report_id)
        if not report:
            return jsonify({'error': 'Fraud report not found'}), 404
        
        complainant = User.query.get(report.complainant_user_id)
        if not complainant:
            return jsonify({'error': 'Complainant not found'}), 404
        
        pending_email_jobs = []
        
        normalized_action = 'verify' if action == 'warn' else action

        if normalized_action == 'verify':
            # Fraud verified - issue warning
            report.status = 'Verified'
            report.action_taken = 'Warning Issued'
            complainant.fraud_warnings += 1

            # Close the fraudulent grievance
            fraud_grievance = Grievance.query.get(report.grievance_id)
            if fraud_grievance:
                fraud_grievance.status = 'Closed'
            
            # Notify complainant
            NotificationService.queue_notification(
                user_id=complainant.id,
                title='Warning: Fraudulent Complaint Verified',
                message=f'Your complaint (Grievance #{report.grievance_id}) has been verified as fraudulent. This is warning #{complainant.fraud_warnings}. Repeated fraudulent complaints will result in account suspension.',
                notification_type='fraud_verified',
                related_grievance_id=report.grievance_id,
                is_read=False,
            )
            pending_email_jobs.append((
                EmailService.send_account_warning_email,
                {
                    'citizen_email': complainant.email,
                    'citizen_name': complainant.name,
                    'grievance_id': report.grievance_id,
                    'warning_count': complainant.fraud_warnings,
                    'reason': admin_notes or report.description,
                }
            ))
            
        elif normalized_action == 'suspend':
            # Suspend account
            report.status = 'Verified'
            report.action_taken = 'Account Suspended'
            complainant.fraud_warnings += 1
            complainant.account_suspended = True
            complainant.suspension_reason = f'Multiple fraudulent complaints. Latest: Grievance #{report.grievance_id}'

            # Close the fraudulent grievance
            fraud_grievance = Grievance.query.get(report.grievance_id)
            if fraud_grievance:
                fraud_grievance.status = 'Closed'
            
            # Notify complainant
            NotificationService.queue_notification(
                user_id=complainant.id,
                title='Account Suspended - Fraudulent Activity',
                message=f'Your account has been suspended due to repeated fraudulent complaints. Contact admin for appeal.',
                notification_type='account_suspended',
                related_grievance_id=report.grievance_id,
                is_read=False,
            )
            pending_email_jobs.append((
                EmailService.send_account_suspension_email,
                {
                    'citizen_email': complainant.email,
                    'citizen_name': complainant.name,
                    'reason': complainant.suspension_reason,
                    'grievance_id': report.grievance_id,
                }
            ))
            
        elif normalized_action == 'dismiss':
            # Fraud report dismissed - complaint was genuine
            report.status = 'Dismissed'
            report.action_taken = 'Report Dismissed - Complaint Genuine'

            # Restore grievance to active workflow
            fraud_grievance = Grievance.query.get(report.grievance_id)
            if fraud_grievance and 'Fraud' in (fraud_grievance.status or ''):
                fraud_grievance.status = 'Assigned to Department'

            NotificationService.queue_notification(
                user_id=complainant.id,
                title='Fraud Review Closed - Complaint Validated',
                message=f'Fraud report for Grievance #{report.grievance_id} has been dismissed. Your complaint remains active.',
                notification_type='fraud_review_closed',
                related_grievance_id=report.grievance_id,
                is_read=False,
            )
            pending_email_jobs.append((
                EmailService.send_fraud_review_notice,
                {
                    'citizen_email': complainant.email,
                    'citizen_name': complainant.name,
                    'grievance_id': report.grievance_id,
                    'stage': 'dismissed',
                    'details': 'Fraud report was dismissed by admin. Your complaint remains valid and in normal workflow.',
                }
            ))
            
        else:
            return jsonify({'error': 'Invalid action'}), 400
        
        report.admin_notes = admin_notes
        report.reviewed_at = datetime.utcnow()
        
        db.session.commit()

        for email_fn, kwargs in pending_email_jobs:
            try:
                email_fn(**kwargs)
            except Exception as email_error:
                print(f"Failed to send fraud-action notification email: {email_error}")
        
        return jsonify({
            'message': f'Action taken successfully: {normalized_action}',
            'complainant_warnings': complainant.fraud_warnings,
            'account_suspended': complainant.account_suspended
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@grievances_bp.route('/check-comment-escalations', methods=['POST'])
def check_comment_escalations():
    """
    Check for overdue comments and escalate them (Admin/System only)
    This endpoint should be called periodically by a cron job or scheduler
    """
    try:
        user, auth_response = get_current_user_from_token(return_error=True, required_roles=['ADMIN'])
        if auth_response:
            return auth_response
        
        # Run escalation check
        escalated_count = check_and_escalate_comments()
        
        return jsonify({
            'message': 'Escalation check completed',
            'escalated_count': escalated_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@grievances_bp.route('/comments/<int:comment_id>/escalate', methods=['POST'])
def manually_escalate_comment(comment_id):
    """
    Manually escalate a specific comment (Admin only)
    """
    try:
        user, auth_response = get_current_user_from_token(return_error=True, required_roles=['ADMIN'])
        if auth_response:
            return auth_response
        
        result = escalate_comment_manually(comment_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

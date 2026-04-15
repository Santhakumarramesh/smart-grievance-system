"""
Comment Escalation Service
Handles automatic escalation of citizen comments when officers don't respond in time
"""
from datetime import datetime
from backend.models import GrievanceComment, Grievance, User, Notification, EscalationLog
from backend.extensions import db
from backend.services.email_service import EmailService
from backend.utils.roles import (
    ADMIN_ROLE_VALUES,
    OFFICER_ROLE_VALUES,
    is_role,
    role_level_for_log,
)


def get_escalation_recipient(current_officer, grievance):
    """
    Resolve escalation target using the active workflow model:
    1. Assigned officer (if different from current notified officer)
    2. Another officer in the same department
    3. Admin fallback
    """
    if not current_officer:
        return None

    if grievance.assigned_officer_id and grievance.assigned_officer_id != current_officer.id:
        assigned_officer = User.query.get(grievance.assigned_officer_id)
        if (
            assigned_officer
            and is_role(assigned_officer, 'OFFICER')
            and assigned_officer.department == grievance.assigned_department
        ):
            return assigned_officer

    department_officer = User.query.filter(
        User.role.in_(OFFICER_ROLE_VALUES),
        User.department == grievance.assigned_department,
        User.id != current_officer.id,
    ).order_by(User.created_at.asc(), User.id.asc()).first()
    if department_officer:
        return department_officer

    return User.query.filter(User.role.in_(ADMIN_ROLE_VALUES)).order_by(User.created_at.asc(), User.id.asc()).first()


def _create_escalation_log(grievance_id, from_officer, to_officer, reason, escalation_type):
    if not to_officer:
        return
    log = EscalationLog(
        grievance_id=grievance_id,
        from_officer_id=from_officer.id if from_officer else None,
        to_officer_id=to_officer.id,
        from_role_level=role_level_for_log(from_officer) if from_officer else 0,
        to_role_level=role_level_for_log(to_officer),
        reason=reason,
        escalation_type=escalation_type,
    )
    db.session.add(log)


def check_and_escalate_comments():
    """
    Check all citizen comments that haven't been responded to
    and escalate to superior if deadline passed
    
    This should be run periodically (e.g., every hour via cron job or scheduler)
    """
    now = datetime.utcnow()
    
    # Find all citizen comments that:
    # 1. Have a response deadline
    # 2. Deadline has passed
    # 3. Haven't been escalated yet
    # 4. Haven't received a response from officer
    
    overdue_comments = GrievanceComment.query.filter(
        GrievanceComment.user_role == 'CITIZEN',
        GrievanceComment.response_deadline.isnot(None),
        GrievanceComment.response_deadline < now,
        GrievanceComment.escalated == False
    ).all()
    
    escalated_count = 0
    updated_any_comment = False
    
    for comment in overdue_comments:
        # Check if officer has responded after this comment
        grievance = Grievance.query.get(comment.grievance_id)
        
        if not grievance:
            continue
        
        # Check if there's an officer response after this citizen comment
        officer_response = GrievanceComment.query.filter(
            GrievanceComment.grievance_id == comment.grievance_id,
            GrievanceComment.created_at > comment.created_at,
            GrievanceComment.user_role.in_(['OFFICER', 'ADMIN'])
        ).first()
        
        if officer_response:
            # Officer has responded, mark as handled
            comment.escalated = True  # Mark as handled (no escalation needed)
            updated_any_comment = True
            continue
        
        # No response from officer - ESCALATE!
        current_officer = None
        if comment.notified_officer_id:
            current_officer = User.query.get(comment.notified_officer_id)
        if not current_officer and grievance.assigned_officer_id:
            current_officer = User.query.get(grievance.assigned_officer_id)
        if not current_officer:
            current_officer = User.query.filter(
                User.role.in_(OFFICER_ROLE_VALUES),
                User.department == grievance.assigned_department,
            ).order_by(User.created_at.asc(), User.id.asc()).first()

        if not current_officer:
            continue

        superior = get_escalation_recipient(current_officer, grievance)
        
        if superior:
            # Mark comment as escalated
            comment.escalated = True
            comment.escalated_at = now
            comment.escalated_to_officer_id = superior.id
            _create_escalation_log(
                grievance_id=grievance.id,
                from_officer=current_officer,
                to_officer=superior,
                reason='No response within 24 hours',
                escalation_type='auto',
            )

            comment_sent_at = (
                comment.notification_sent_at.strftime('%Y-%m-%d %H:%M')
                if comment.notification_sent_at else 'N/A'
            )
            response_deadline = (
                comment.response_deadline.strftime('%Y-%m-%d %H:%M')
                if comment.response_deadline else 'N/A'
            )
            
            # Send email to superior
            EmailService.send_email(
                superior.email,
                f'⚠️ ESCALATED: Comment on Grievance #{grievance.id} - No Response from {current_officer.name}',
                f"""
Dear {superior.name},

This is an escalation alert. A citizen comment on Grievance #{grievance.id} has not been responded to by {current_officer.name} within the required timeframe.

Citizen's Comment:
"{comment.comment_text}"

Comment was sent: {comment_sent_at}
Response deadline: {response_deadline}

Please review and take necessary action immediately.

View grievance: {EmailService.tracking_url(grievance.id)}

Best regards,
Smart Grievance System
                """
            )
            
            # Create in-app notification for superior
            notification = Notification(
                user_id=superior.id,
                title=f'⚠️ Escalated: Grievance #{grievance.id}',
                message=f'Comment from citizen not responded by {current_officer.name}. Requires immediate attention.',
                notification_type='escalation',
                related_grievance_id=grievance.id
            )
            db.session.add(notification)
            
            # Notify the original officer about escalation
            EmailService.send_email(
                current_officer.email,
                f'⚠️ Your case has been escalated - Grievance #{grievance.id}',
                f"""
Dear {current_officer.name},

Your assigned grievance #{grievance.id} has been escalated to {superior.name} due to no response within the required 24-hour timeframe.

Please coordinate with your superior and respond promptly to citizen comments in the future.

View grievance: {EmailService.tracking_url(grievance.id)}

Best regards,
Smart Grievance System
                """
            )
            
            escalated_count += 1
            updated_any_comment = True
    
    # Commit all changes
    if updated_any_comment:
        db.session.commit()
        if escalated_count > 0:
            print(f"✓ Escalated {escalated_count} overdue comments")
    
    return escalated_count


def escalate_comment_manually(comment_id):
    """
    Manually escalate a specific comment
    Used when admin wants to force escalation
    
    Args:
        comment_id: ID of the comment to escalate
    
    Returns:
        dict with success status and message
    """
    comment = GrievanceComment.query.get(comment_id)
    
    if not comment:
        return {'success': False, 'message': 'Comment not found'}
    
    if comment.user_role != 'CITIZEN':
        return {'success': False, 'message': 'Only citizen comments can be escalated'}
    
    if comment.escalated:
        return {'success': False, 'message': 'Comment already escalated'}
    
    grievance = Grievance.query.get(comment.grievance_id)
    
    if not grievance:
        return {'success': False, 'message': 'Grievance not found'}
    
    current_officer = None
    if comment.notified_officer_id:
        current_officer = User.query.get(comment.notified_officer_id)
    if not current_officer and grievance.assigned_officer_id:
        current_officer = User.query.get(grievance.assigned_officer_id)
    
    if not current_officer:
        return {'success': False, 'message': 'No officer assigned'}
    
    superior = get_escalation_recipient(current_officer, grievance)
    
    if not superior:
        return {'success': False, 'message': 'No superior officer found for escalation'}
    
    # Mark as escalated
    comment.escalated = True
    comment.escalated_at = datetime.utcnow()
    comment.escalated_to_officer_id = superior.id
    _create_escalation_log(
        grievance_id=grievance.id,
        from_officer=current_officer,
        to_officer=superior,
        reason='Manual escalation by admin',
        escalation_type='manual',
    )
    
    # Send notifications
    EmailService.send_email(
        superior.email,
        f'⚠️ MANUALLY ESCALATED: Grievance #{grievance.id}',
        f"""
Dear {superior.name},

A comment on Grievance #{grievance.id} has been manually escalated to you.

Citizen's Comment:
"{comment.comment_text}"

Please review and take action.

View grievance: {EmailService.tracking_url(grievance.id)}

Best regards,
Smart Grievance System
        """
    )
    
    db.session.commit()
    
    return {
        'success': True,
        'message': f'Comment escalated to {superior.name}',
        'escalated_to': superior.name
    }

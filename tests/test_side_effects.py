import pytest
from datetime import datetime, timedelta
import json
from backend.extensions import db
from backend.models import Grievance, User, FraudReport, RoleHierarchy, Notification
from backend.routes.auth import create_access_token
from backend.services.scheduler import scan_sla_breaches
from backend.services.notification_service import NotificationService
from backend.services.email_service import EmailService

def auth_headers(user_id):
    return {"Authorization": f"Bearer {create_access_token(user_id)}"}

def create_user_for_test(name, email, phone, role="CITIZEN", department=None, password="Password123", suspended=False):
    user = User(
        name=name,
        email=email,
        phone=phone,
        role=role,
        department=department,
        email_verified=True,
        phone_verified=True,
        account_suspended=suspended
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

def create_grievance_for_test(user_id, department, status="Received", assigned_officer_id=None, sla_breached=False):
    grievance = Grievance(
        user_id=user_id,
        complaint_text="Test complaint text.",
        predicted_department=department,
        assigned_department=department,
        status=status,
        assigned_officer_id=assigned_officer_id,
        location="Test Loc",
        sla_breached=sla_breached,
        sla_deadline=datetime.utcnow() - timedelta(hours=1) if sla_breached else datetime.utcnow() + timedelta(hours=48)
    )
    db.session.add(grievance)
    db.session.commit()
    return grievance

# 1. SLA Breach Scan Side Effects Verification
def test_sla_breach_scanner_emits_notifications(client, app, monkeypatch):
    calls = []
    
    def mock_queue_notification(**kwargs):
        calls.append(kwargs)
        return True
        
    monkeypatch.setattr(NotificationService, 'queue_notification', mock_queue_notification)
    
    with app.app_context():
        # Clean any existing users that could be admins to make test deterministic
        User.query.filter_by(role='ADMIN').delete()
        db.session.commit()
        
        citizen = create_user_for_test("SLA Citizen", "slactz@example.com", "9111111001")
        officer = create_user_for_test("SLA Officer", "slaoff@example.com", "9111111002", role="OFFICER", department="Water Supply")
        admin = create_user_for_test("SLA Admin", "sladmin@example.com", "9111111003", role="ADMIN")
        
        g = Grievance(
            user_id=citizen.id,
            complaint_text="Overdue SLA complaint",
            predicted_department="Water Supply",
            assigned_department="Water Supply",
            status="Assigned to Department",
            assigned_officer_id=officer.id,
            sla_breached=False,
            sla_deadline=datetime.utcnow() - timedelta(hours=2)
        )
        db.session.add(g)
        db.session.commit()
        
        # Action!
        scan_sla_breaches()
        
        # Verify db state first
        db.session.expire_all()
        g_updated = db.session.get(Grievance, g.id)
        assert g_updated.sla_breached is True
        assert g_updated.sla_breached_at is not None

    # We expect 2 notifications queued: one for assigned officer, one for admin
    assert len(calls) == 2
    
    # Check officer notification
    off_call = next(c for c in calls if c['user_id'] == officer.id)
    assert off_call['notification_type'] == 'sla_breach'
    assert 'exceeded' in off_call['message'].lower()
    
    # Check admin notification
    adm_call = next(c for c in calls if c['user_id'] == admin.id)
    assert adm_call['notification_type'] == 'sla_breach'
    assert 'Water Supply' in adm_call['message']


# 2. Fraud Verified Flow Side Effects
def test_fraud_verified_emits_warnings_and_emails(client, app, monkeypatch):
    queue_calls = []
    email_calls = []
    
    def mock_queue_notification(**kwargs):
        queue_calls.append(kwargs)
        return True
        
    def mock_send_account_warning_email(**kwargs):
        email_calls.append(kwargs)
        return True
        
    monkeypatch.setattr(NotificationService, 'queue_notification', mock_queue_notification)
    monkeypatch.setattr(EmailService, 'send_account_warning_email', mock_send_account_warning_email)
    
    with app.app_context():
        admin = create_user_for_test("Fraud Admin", "fraud_adm1@example.com", "9111111004", role="ADMIN")
        citizen = create_user_for_test("Fraud Citizen", "fraud_ctz1@example.com", "9111111005")
        
        g = create_grievance_for_test(citizen.id, "Police", status="Suspended - Fraud Investigation")
        
        report = FraudReport(
            grievance_id=g.id,
            reported_by_officer_id=admin.id,
            complainant_user_id=citizen.id,
            fraud_type="Fake Complaint",
            description="Testing verify side effects",
            status="Pending"
        )
        db.session.add(report)
        db.session.commit()
        
        report_id = report.id
        admin_id = admin.id
        citizen_id = citizen.id
        g_id = g.id

    payload = {"action": "verify", "admin_notes": "Confirmed fake issue", "suspend_user": False}
    # Using the real route from grievances.py /fraud-reports/<id>/action
    resp = client.post(f"/api/grievances/fraud-reports/{report_id}/action", json=payload, headers=auth_headers(admin_id))
    assert resp.status_code == 200
    
    # Assert DB changes
    with app.app_context():
        ctz = db.session.get(User, citizen_id)
        assert ctz.fraud_warnings == 1
        assert ctz.account_suspended is False
        
        updated_g = db.session.get(Grievance, g_id)
        assert updated_g.status == "Closed"

    # Assert side effects
    assert len(queue_calls) == 1
    assert queue_calls[0]['user_id'] == citizen_id
    assert queue_calls[0]['notification_type'] == 'fraud_verified'
    
    assert len(email_calls) == 1
    assert email_calls[0]['citizen_email'] == "fraud_ctz1@example.com"
    assert email_calls[0]['warning_count'] == 1


# 3. Fraud Dismissed Flow Side Effects
def test_fraud_dismissed_emits_notifications(client, app, monkeypatch):
    queue_calls = []
    def mock_queue_notification(**kwargs):
        queue_calls.append(kwargs)
        return True
        
    monkeypatch.setattr(NotificationService, 'queue_notification', mock_queue_notification)
    
    with app.app_context():
        admin = create_user_for_test("Fraud Admin2", "fraud_adm2@example.com", "9111111006", role="ADMIN")
        citizen = create_user_for_test("Fraud Citizen2", "fraud_ctz2@example.com", "9111111007")
        
        g = create_grievance_for_test(citizen.id, "Police", status="Suspended - Fraud Investigation")
        
        report = FraudReport(
            grievance_id=g.id,
            reported_by_officer_id=admin.id,
            complainant_user_id=citizen.id,
            fraud_type="Fake Complaint",
            description="Testing dismiss side effects",
            status="Pending"
        )
        db.session.add(report)
        db.session.commit()
        
        report_id = report.id
        admin_id = admin.id
        citizen_id = citizen.id
        g_id = g.id

    payload = {"action": "dismiss", "admin_notes": "It is real"}
    resp = client.post(f"/api/grievances/fraud-reports/{report_id}/action", json=payload, headers=auth_headers(admin_id))
    assert resp.status_code == 200
    
    with app.app_context():
        updated_g = db.session.get(Grievance, g_id)
        assert updated_g.status == "Assigned to Department"
        
    assert len(queue_calls) == 1
    assert queue_calls[0]['notification_type'] == 'fraud_review_closed'
    assert queue_calls[0]['user_id'] == citizen_id


# 4. Unsuspend Flow Side Effects
def test_unsuspend_emits_notifications_and_audit(client, app, monkeypatch):
    queue_calls = []
    def mock_queue_notification(**kwargs):
        queue_calls.append(kwargs)
        return True
        
    monkeypatch.setattr(NotificationService, 'queue_notification', mock_queue_notification)
    
    with app.app_context():
        admin = create_user_for_test("Unsuspend Admin", "unsusp_adm@example.com", "9111111008", role="ADMIN")
        citizen = create_user_for_test("Unsusp Citizen", "unsusp_ctz@example.com", "9111111009", suspended=True)
        citizen.suspension_reason = "Too many fakes"
        citizen.fraud_warnings = 3
        db.session.commit()
        
        admin_id = admin.id
        citizen_id = citizen.id
        
    payload = {"admin_notes": "User provided sufficient proof over physical mail.", "reset_warnings": True}
    resp = client.post(f"/api/admin/unsuspend-user/{citizen_id}", json=payload, headers=auth_headers(admin_id))
    assert resp.status_code == 200
    
    with app.app_context():
        ctz = db.session.get(User, citizen_id)
        assert ctz.account_suspended is False
        assert ctz.fraud_warnings == 0
        assert ctz.suspension_reason is None
        
    # Unsuspend route creates notifications in NotificationService
    assert len(queue_calls) == 1
    assert queue_calls[0]['user_id'] == citizen_id
    assert queue_calls[0]['notification_type'] == 'account_reinstated'

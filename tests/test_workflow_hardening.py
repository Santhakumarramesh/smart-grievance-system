import pytest
from datetime import datetime, timedelta
import json
from backend.extensions import db
from backend.models import Grievance, User, FraudReport, RoleHierarchy
from backend.routes.auth import create_access_token
from backend.services.content_moderator import ContentModerator
from backend.services.scheduler import scan_sla_breaches

def auth_headers(user_id):
    return {"Authorization": f"Bearer {create_access_token(user_id)}"}

def create_user(name, email, phone, role="CITIZEN", department=None, password="Password123", suspended=False):
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

# --- Content Moderation Integration Tests ---

def test_moderation_high_severity_blocks(client, app, monkeypatch):
    with app.app_context():
        citizen = create_user("Block Test", "block@example.com", "9111111111")
        user_id = citizen.id
        
    def mock_moderate_high(*args, **kwargs):
        return {'is_safe': False, 'score': 45, 'severity': 'high', 'flags': ['threats']}
    
    monkeypatch.setattr(ContentModerator, "moderate_content", mock_moderate_high)
    
    payload = {
        "complaint_text": "I will destroy everything",
        "department": "Water Supply",
        "location": "Test Loc"
    }
    
    resp = client.post("/api/grievances/submit", json=payload, headers=auth_headers(user_id))
    assert resp.status_code == 400
    assert "inappropriate" in resp.get_json()["error"].lower()

def test_moderation_medium_severity_flags(client, app, monkeypatch):
    with app.app_context():
        citizen = create_user("Flag Test", "flag@example.com", "9111111112")
        user_id = citizen.id
        
    def mock_moderate_med(*args, **kwargs):
        return {'is_safe': False, 'score': 20, 'severity': 'medium', 'flags': ['profanity']}
    
    monkeypatch.setattr(ContentModerator, "moderate_content", mock_moderate_med)
    
    payload = {
        "complaint_text": "This service is absolute garbage",
        "department": "Water Supply",
        "location": "Test Loc"
    }
    
    resp = client.post("/api/grievances/submit", json=payload, headers=auth_headers(user_id))
    assert resp.status_code == 201
    
    with app.app_context():
        g = Grievance.query.filter_by(user_id=user_id).first()
        assert g.is_flagged is True
        assert g.moderation_severity == "medium"
        assert g.moderation_score == 20

# --- SLA Logic Tests ---

def test_sla_logic_populates_deadline(client, app):
    with app.app_context():
        citizen = create_user("SLA Test", "sla@example.com", "9111111113")
        user_id = citizen.id
        
        # Create department config
        role = RoleHierarchy(department="Electricity", role_name="Engineer", role_level=1, sla_hours=24)
        db.session.add(role)
        db.session.commit()
        
    payload = {
        "complaint_text": "Power cut in Sector 4",
        "department": "Electricity",
        "location": "Sector 4"
    }
    
    resp = client.post("/api/grievances/submit", json=payload, headers=auth_headers(user_id))
    assert resp.status_code == 201
    
    with app.app_context():
        g = Grievance.query.filter_by(user_id=user_id).first()
        assert g.sla_deadline is not None
        # It should be approx 24 hours from created_at
        diff_hours = (g.sla_deadline - g.created_at).total_seconds() / 3600
        assert 23.9 <= diff_hours <= 24.1

def test_sla_breach_scanner_marks_overdue(client, app):
    with app.app_context():
        citizen = create_user("Breach Test", "breach@example.com", "9111111114")
        g = Grievance(
            user_id=citizen.id,
            complaint_text="Overdue complaint",
            predicted_department="Water Supply",
            assigned_department="Water Supply",
            status="Received",
            sla_deadline=datetime.utcnow() - timedelta(hours=1),
            last_action_at=datetime.utcnow() - timedelta(hours=2)
        )
        db.session.add(g)
        db.session.commit()
        g_id = g.id
        
        scan_sla_breaches(app)
        
        updated_g = db.session.get(Grievance, g_id)
        assert updated_g.sla_breached is True
        assert updated_g.sla_breached_at is not None

# --- Fraud Lifecycle Tests ---

def test_fraud_verified_closes_grievance(client, app):
    with app.app_context():
        admin = create_user("Admin Fraud", "admin_f@example.com", "9000000001", role="ADMIN")
        citizen = create_user("Fraud User", "fraud@example.com", "9000000002")
        g = Grievance(
            user_id=citizen.id,
            complaint_text="Fake stuff",
            predicted_department="Police",
            assigned_department="Police",
            status="Received"
        )
        db.session.add(g)
        db.session.commit()
        
        report = FraudReport(
            grievance_id=g.id,
            reported_by_officer_id=admin.id,
            complainant_user_id=citizen.id,
            fraud_type="Fake Complaint",
            description="Testing fraud",
            status="Pending"
        )
        db.session.add(report)
        db.session.commit()
        report_id = report.id
        g_id = g.id
        admin_id = admin.id

    payload = {
        "action": "verify",
        "admin_notes": "Confirmed it is fake",
        "suspend_user": False
    }
    resp = client.post(f"/api/admin/fraud-reports/{report_id}/review", json=payload, headers=auth_headers(admin_id))
    assert resp.status_code == 200
    
    with app.app_context():
        g_updated = db.session.get(Grievance, g_id)
        assert g_updated.status == "Closed"

def test_fraud_dismissed_restores_status(client, app):
    with app.app_context():
        admin = create_user("Admin Fraud2", "admin_f2@example.com", "9000000003", role="ADMIN")
        citizen = create_user("Fraud User2", "fraud2@example.com", "9000000004")
        g = Grievance(
            user_id=citizen.id,
            complaint_text="Real stuff actually",
            predicted_department="Police",
            assigned_department="Police",
            status="Suspended - Fraud Investigation"
        )
        db.session.add(g)
        db.session.commit()
        
        report = FraudReport(
            grievance_id=g.id,
            reported_by_officer_id=admin.id,
            complainant_user_id=citizen.id,
            fraud_type="Fake Complaint",
            description="Testing dismiss",
            status="Pending"
        )
        db.session.add(report)
        db.session.commit()
        report_id = report.id
        g_id = g.id
        admin_id = admin.id

    payload = {
        "action": "dismiss",
        "admin_notes": "It is real"
    }
    resp = client.post(f"/api/admin/fraud-reports/{report_id}/review", json=payload, headers=auth_headers(admin_id))
    assert resp.status_code == 200
    
    with app.app_context():
        g_updated = db.session.get(Grievance, g_id)
        assert g_updated.status == "Assigned to Department"

# --- Unsuspend User Tests ---

def test_unsuspend_user_endpoint_missing_notes(client, app):
    with app.app_context():
        admin = create_user("Admin Unsuspend1", "admin_u1@example.com", "9000000005", role="ADMIN")
        citizen = create_user("SuspUser1", "susp1@example.com", "9000000006", suspended=True)
        db.session.commit()
        admin_id = admin.id
        citizen_id = citizen.id
        
    payload = {
        "admin_notes": "ok" # too short
    }
    resp = client.post(f"/api/admin/unsuspend-user/{citizen_id}", json=payload, headers=auth_headers(admin_id))
    assert resp.status_code == 400
    assert "admin_notes is required" in resp.get_json()["error"]

def test_unsuspend_user_endpoint_success(client, app):
    with app.app_context():
        admin = create_user("Admin Unsuspend2", "admin_u2@example.com", "9000000007", role="ADMIN")
        citizen = create_user("SuspUser2", "susp2@example.com", "9000000008", suspended=True)
        citizen.suspension_reason = "Too many frauds"
        citizen.fraud_warnings = 3
        db.session.commit()
        admin_id = admin.id
        citizen_id = citizen.id
        
    payload = {
        "admin_notes": "User appealed and showed proof.",
        "reset_warnings": True
    }
    resp = client.post(f"/api/admin/unsuspend-user/{citizen_id}", json=payload, headers=auth_headers(admin_id))
    assert resp.status_code == 200
    
    with app.app_context():
        user = db.session.get(User, citizen_id)
        assert user.account_suspended is False
        assert user.suspension_reason is None
        assert user.fraud_warnings == 0

from backend.extensions import db
from backend.models import User
from backend.routes.auth import create_access_token, create_reset_token


def create_user(name, email, phone, role="CITIZEN", password="Password123"):
    user = User(
        name=name,
        email=email,
        phone=phone,
        role=role,
        email_verified=True,
        phone_verified=True,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_unauthorized_access_returns_consistent_auth_error(client):
    response = client.get("/api/grievances/my-grievances")
    assert response.status_code == 401
    payload = response.get_json()
    assert payload["error"] == "Unauthorized"
    assert payload["code"] == "auth_missing_token"


def test_suspended_user_login_and_api_access_blocked(client, app):
    with app.app_context():
        user = create_user("Suspended Citizen", "suspended@example.com", "9876511111")
        user.account_suspended = True
        user.suspension_reason = "Fraud investigation"
        db.session.commit()
        access_token = create_access_token(user.id)

    login_response = client.post(
        "/api/auth/login",
        json={"email": "suspended@example.com", "password": "Password123"},
    )
    assert login_response.status_code == 403
    assert login_response.get_json()["code"] == "auth_account_suspended"

    protected_response = client.get(
        "/api/grievances/my-grievances",
        headers=auth_headers(access_token),
    )
    assert protected_response.status_code == 403
    assert protected_response.get_json()["code"] == "auth_account_suspended"


def test_lockout_after_repeated_failed_login_attempts(client, app):
    with app.app_context():
        create_user("Lockout User", "lockout@example.com", "9876522222", password="StrongPass123")

    for _ in range(3):
        failed = client.post(
            "/api/auth/login",
            json={"email": "lockout@example.com", "password": "WrongPass123"},
        )
        assert failed.status_code == 401

    locked = client.post(
        "/api/auth/login",
        json={"email": "lockout@example.com", "password": "WrongPass123"},
    )
    assert locked.status_code == 429
    assert locked.get_json()["error"] == "Account temporarily locked"


def test_invalid_token_type_usage_rejected(client, app):
    with app.app_context():
        user = create_user("Token User", "tokenuser@example.com", "9876533333")
        reset_token = create_reset_token(user.id)
        access_token = create_access_token(user.id)

    me_with_reset = client.get("/api/auth/me", headers=auth_headers(reset_token))
    assert me_with_reset.status_code == 401
    assert me_with_reset.get_json()["code"] == "auth_invalid_token"

    refresh_with_access = client.post(
        "/api/auth/refresh-token",
        json={"refresh_token": access_token},
    )
    assert refresh_with_access.status_code == 401
    assert refresh_with_access.get_json()["code"] == "auth_invalid_refresh_token"


def test_malformed_input_payloads_rejected(client, app):
    with app.app_context():
        user = create_user("Valid User", "validuser@example.com", "9876544444")
        token = create_access_token(user.id)

    invalid_profile = client.put(
        "/api/auth/profile/update",
        json={"gender": "UnknownGenderValue"},
        headers=auth_headers(token),
    )
    assert invalid_profile.status_code == 400
    assert "gender must be one of" in invalid_profile.get_json()["error"]

    invalid_complaint = client.post(
        "/api/grievances/submit",
        json={
            "complaint_text": "<script>alert('x')</script>this is enough complaint text content",
            "location": "Ward 9, Main Street near public office",
            "images": [],
        },
        headers=auth_headers(token),
    )
    assert invalid_complaint.status_code == 400
    assert "prohibited content" in invalid_complaint.get_json()["error"]

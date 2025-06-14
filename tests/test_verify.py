import json
from app.models import User
from werkzeug.security import generate_password_hash

def test_verify_password_success(client, monkeypatch):
    """
    Test password verification with correct credentials.
    """
    # Create user in DB
    user = User.create(
        email="verify@example.com",
        hashed_passwd=generate_password_hash("goodpassword"),
        firstname="Verify",
        lastname="User",
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1
    )
    # Simulate internal auth header if needed by @require_internal
    headers = {"X-Internal-Auth": "1"}
    data = {"email": "verify@example.com", "password": "goodpassword"}
    response = client.post(
        "/users/verify_password",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers
    )
    assert response.status_code == 200
    assert response.json["valid"] is True
    assert response.json["user_id"] == user.id
    assert response.json["company_id"] == user.company_id

def test_verify_password_wrong_password(client):
    """
    Test password verification with wrong password.
    """
    User.create(
        email="wrongpass@example.com",
        hashed_passwd=generate_password_hash("rightpassword"),
        firstname="Wrong",
        lastname="Pass",
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1
    )
    headers = {"X-Internal-Auth": "1"}
    data = {"email": "wrongpass@example.com", "password": "badpassword"}
    response = client.post(
        "/users/verify_password",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers
    )
    assert response.status_code == 401
    assert response.json["valid"] is False

def test_verify_password_user_not_found(client):
    """
    Test password verification with unknown email.
    """
    headers = {"X-Internal-Auth": "1"}
    data = {"email": "notfound@example.com", "password": "any"}
    response = client.post(
        "/users/verify_password",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers
    )
    assert response.status_code == 404
    assert response.json["valid"] is False

def test_verify_password_missing_fields(client):
    """
    Test password verification with missing fields.
    """
    headers = {"X-Internal-Auth": "1"}
    data = {"email": "missing@example.com"}
    response = client.post(
        "/users/verify_password",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers
    )
    assert response.status_code == 400
    assert "message" in response.json
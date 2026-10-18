import uuid

from app.models.user import User
from app.services.security import verify_password


def test_register_success(client, db_session):
    email = f"{uuid.uuid4().hex}@example.com"
    password = "SecurePass123!"

    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password},
    )

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == email
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data

    user = db_session.query(User).filter_by(email=email).one()

    assert user.password_hash != password
    assert verify_password(password, user.password_hash)


def test_register_duplicate_email_returns_409(client):
    email = f"{uuid.uuid4().hex}@example.com"
    payload = {
        "email": email,
        "password": "SecurePass123!",
    }

    first_response = client.post("/api/auth/register", json=payload)
    second_response = client.post("/api/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already registered"


def test_register_short_password_returns_422(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": f"{uuid.uuid4().hex}@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422


def test_register_invalid_email_returns_422(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "not-an-email",
            "password": "SecurePass123!",
        },
    )

    assert response.status_code == 422

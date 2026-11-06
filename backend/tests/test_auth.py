import uuid

import jwt

from app.core.config import settings
from app.models.user import User
from app.services.security import verify_password


def registration_payload(email: str, password: str = "SecurePass123!") -> dict:
    return {
        "email": email,
        "password": password,
        "timezone": "Asia/Bangkok",
    }


def test_register_success(client, db_session):
    email = f"{uuid.uuid4().hex}@example.com"
    response = client.post("/api/auth/register", json=registration_payload(email))

    assert response.status_code == 201
    data = response.json()["user"]
    assert data["email"] == email
    assert data["displayName"] == email
    assert data["timezone"] == "Asia/Bangkok"
    assert "password_hash" not in data

    user = db_session.query(User).filter_by(email=email).one()
    assert verify_password("SecurePass123!", user.password_hash)

    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "SecurePass123!"},
    )
    assert login_response.status_code == 200


def test_register_duplicate_email_returns_409(client):
    email = f"{uuid.uuid4().hex}@example.com"
    payload = registration_payload(email)
    assert client.post("/api/auth/register", json=payload).status_code == 201

    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"


def test_register_validation_errors_return_422(client):
    assert client.post(
        "/api/auth/register",
        json=registration_payload(f"{uuid.uuid4().hex}@example.com", "short"),
    ).status_code == 422
    assert client.post(
        "/api/auth/register",
        json=registration_payload("not-an-email"),
    ).status_code == 422


def test_login_wrong_password_returns_401(client):
    email = f"{uuid.uuid4().hex}@example.com"
    client.post("/api/auth/register", json=registration_payload(email))

    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "WrongPassword123!"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_returns_access_and_refresh_tokens(client):
    email = f"{uuid.uuid4().hex}@example.com"
    register_response = client.post(
        "/api/auth/register",
        json=registration_payload(email),
    )

    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "SecurePass123!", "rememberMe": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["accessToken"]
    assert data["refreshToken"]
    assert data["tokenType"] == "bearer"
    assert data["expiresIn"] == 900

    claims = jwt.decode(
        data["accessToken"],
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    assert claims["sub"] == register_response.json()["user"]["id"]
    assert claims["type"] == "access"


def test_refresh_rotates_token_and_logout_revokes_session(client):
    email = f"{uuid.uuid4().hex}@example.com"
    client.post("/api/auth/register", json=registration_payload(email))
    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "SecurePass123!"},
    )
    refresh_token = login_response.json()["refreshToken"]

    refresh_response = client.post(
        "/api/auth/refresh",
        json={"refreshToken": refresh_token},
    )
    assert refresh_response.status_code == 200
    rotated_token = refresh_response.json()["refreshToken"]
    assert rotated_token != refresh_token

    assert client.post(
        "/api/auth/refresh",
        json={"refreshToken": refresh_token},
    ).status_code == 401

    assert client.post(
        "/api/auth/logout",
        json={"refreshToken": rotated_token},
    ).status_code == 204
    assert client.post(
        "/api/auth/refresh",
        json={"refreshToken": rotated_token},
    ).status_code == 401


def test_me_returns_current_user_and_blocks_locked_user(client, db_session):
    email = f"{uuid.uuid4().hex}@example.com"
    register_response = client.post(
        "/api/auth/register",
        json=registration_payload(email),
    )
    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "SecurePass123!"},
    )
    access_token = login_response.json()["accessToken"]

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["user"]["id"] == register_response.json()["user"]["id"]

    user = db_session.query(User).filter_by(email=email).one()
    user.status = "LOCKED"
    db_session.commit()
    assert client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    ).status_code == 401


def test_protected_endpoint_without_token_returns_401(client):
    assert client.get("/api/auth/me").status_code == 401

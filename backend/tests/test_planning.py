from datetime import date, datetime, timezone

from app.models.user import User
from app.services.security import hash_password


def _login(client, db_session):
    user = User(
        email="planning@example.com",
        password_hash=hash_password("Password123!"),
        display_name="Planning User",
        timezone="Asia/Bangkok",
        status="ACTIVE",
        email_verified_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    db_session.commit()
    response = client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "Password123!", "rememberMe": False},
    )
    return {"Authorization": f"Bearer {response.json()['accessToken']}"}


def test_rejected_proposal_keeps_schedule_unchanged(client, db_session):
    headers = _login(client, db_session)
    activity = client.post(
        "/api/activities",
        headers=headers,
        json={"title": "ทำรายงาน", "dateStart": str(date.today()), "durationMinutes": 60},
    )
    assert activity.status_code == 201

    before = client.get("/api/schedule", headers=headers).json()
    request = client.post(
        "/api/planning/requests",
        headers=headers,
        json={"inputText": "จัดตารางกิจกรรมวันนี้"},
    )
    assert request.status_code == 201
    rejected = client.post(
        f"/api/proposals/{request.json()['proposalId']}/reject",
        headers=headers,
        json={"reason": "ขอแก้เวลาเอง"},
    )
    assert rejected.json()["status"] == "REJECTED"
    after = client.get("/api/schedule", headers=headers).json()
    assert after == before


def test_confirmed_proposal_creates_new_schedule_version(client, db_session):
    headers = _login(client, db_session)
    activity = client.post(
        "/api/activities",
        headers=headers,
        json={"title": "อ่านหนังสือ", "dateStart": str(date.today()), "durationMinutes": 60},
    )
    assert activity.status_code == 201
    request = client.post(
        "/api/planning/requests",
        headers=headers,
        json={"inputText": "จัดตารางกิจกรรม"},
    )
    proposal_id = request.json()["proposalId"]
    confirmed = client.post(f"/api/proposals/{proposal_id}/confirm", headers=headers, json={})
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "CONFIRMED"
    schedule = client.get("/api/schedule", headers=headers).json()
    assert schedule["scheduleVersion"]["versionNumber"] == 1
    assert len(schedule["items"]) == 1

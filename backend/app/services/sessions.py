from datetime import datetime, timedelta, timezone
import uuid

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.auth_session import AuthSession
from app.models.auth_token import AuthToken
from app.services.security import create_random_token, hash_token

REFRESH_TOKEN_TYPE = "REFRESH"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def session_lifetime(remember_me: bool) -> timedelta:
    return timedelta(days=30 if remember_me else 7)


def create_session(
    db: Session,
    user_id: uuid.UUID,
    remember_me: bool,
    device_info: dict | None = None,
) -> tuple[AuthSession, str]:
    now = _now()
    lifetime = session_lifetime(remember_me)
    expires_at = now + lifetime
    session = AuthSession(
        user_id=user_id,
        remember_me=remember_me,
        expires_at=expires_at,
        absolute_expires_at=expires_at,
        device_info=device_info,
        last_used_at=now,
    )
    db.add(session)
    db.flush()

    raw_token = create_random_token()
    db.add(
        AuthToken(
            user_id=user_id,
            session_id=session.id,
            token_type=REFRESH_TOKEN_TYPE,
            token_hash=hash_token(raw_token),
            expires_at=expires_at,
        )
    )
    return session, raw_token


def rotate_refresh_token(
    db: Session,
    raw_token: str,
) -> tuple[AuthSession, str] | None:
    now = _now()
    token = (
        db.query(AuthToken)
        .filter(
            AuthToken.token_hash == hash_token(raw_token),
            AuthToken.token_type == REFRESH_TOKEN_TYPE,
            AuthToken.used_at.is_(None),
        )
        .one_or_none()
    )
    if token is None or token.expires_at <= now or token.session_id is None:
        return None

    session = db.get(AuthSession, token.session_id)
    if (
        session is None
        or session.revoked_at is not None
        or session.expires_at <= now
        or session.absolute_expires_at <= now
    ):
        return None

    token.used_at = now
    session.last_used_at = now
    next_token = create_random_token()
    db.add(
        AuthToken(
            user_id=session.user_id,
            session_id=session.id,
            token_type=REFRESH_TOKEN_TYPE,
            token_hash=hash_token(next_token),
            expires_at=session.absolute_expires_at,
        )
    )
    db.flush()
    return session, next_token


def revoke_session(db: Session, raw_token: str) -> bool:
    token = (
        db.query(AuthToken)
        .filter(
            AuthToken.token_hash == hash_token(raw_token),
            AuthToken.token_type == REFRESH_TOKEN_TYPE,
        )
        .one_or_none()
    )
    if token is None or token.session_id is None:
        return False

    session = db.get(AuthSession, token.session_id)
    if session is None:
        return False

    if session.revoked_at is None:
        session.revoked_at = _now()
    return True


def revoke_user_sessions(db: Session, user_id: uuid.UUID) -> None:
    now = _now()
    db.query(AuthSession).filter(
        AuthSession.user_id == user_id,
        AuthSession.revoked_at.is_(None),
    ).update({"revoked_at": now}, synchronize_session=False)

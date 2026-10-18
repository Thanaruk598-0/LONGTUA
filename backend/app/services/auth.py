from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.security import hash_password


def register_user(
    db: Session,
    email: str,
    password: str,
) -> User:
    normalized_email = email.strip().lower()

    user = User(
        email=normalized_email,
        password_hash=hash_password(password),
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Email already registered") from None

    db.refresh(user)
    return user

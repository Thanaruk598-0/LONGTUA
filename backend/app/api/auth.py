from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    UserResponseEnvelope,
)
from app.services.auth import authenticate_user, register_user
from app.services.security import create_access_token
from app.services.sessions import (
    create_session,
    revoke_session,
    rotate_refresh_token,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponseEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
) -> UserResponseEnvelope:
    try:
        user = register_user(
            db=db,
            email=str(payload.email),
            password=payload.password,
            display_name=payload.display_name,
            timezone=payload.timezone,
        )
    except ValueError as exc:
        db.rollback()
        error_status = (
            status.HTTP_409_CONFLICT
            if str(exc) == "Email already registered"
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=error_status, detail=str(exc)) from exc
    return UserResponseEnvelope(user=UserResponse.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = authenticate_user(db=db, email=str(payload.email), password=payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email verification is required",
        )

    session, refresh_token = create_session(db, user.id, payload.remember_me)
    db.commit()
    return TokenResponse(
        access_token=create_access_token(subject=str(user.id)),
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    payload: RefreshRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    result = rotate_refresh_token(db, payload.refresh_token)
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh session")

    session, refresh_token = result
    user = db.get(User, session.user_id)
    if user is None or user.status != "ACTIVE":
        db.rollback()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh session")

    db.commit()
    return TokenResponse(
        access_token=create_access_token(subject=str(user.id)),
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: RefreshRequest,
    db: Session = Depends(get_db),
) -> Response:
    revoke_session(db, payload.refresh_token)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.get("/me", response_model=UserResponseEnvelope)
def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponseEnvelope:
    return UserResponseEnvelope(user=UserResponse.model_validate(current_user))

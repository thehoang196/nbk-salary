"""
NBK Salary API - Authentication Router

Provides endpoints for user login, registration, current user retrieval,
user listing, and user activation/deactivation.
Implements account lockout after 5 failed login attempts (15-minute lock).
"""

import re
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from app.utils.auth import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.utils.dependencies import get_current_user, require_role

router = APIRouter(prefix="/auth", tags=["auth"])

LOCKOUT_THRESHOLD = 5
LOCKOUT_DURATION_MINUTES = 15


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token.

    - Checks account lock status
    - Verifies credentials
    - On failure: increments failed_login_count; locks after 5 failures
    - On success: resets failed_login_count and returns token
    """
    user = db.query(User).filter(User.username == request.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is locked due to too many failed login attempts. Try again later.",
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive",
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        # Increment failed login count
        user.failed_login_count = (user.failed_login_count or 0) + 1

        # Lock account if threshold reached
        if user.failed_login_count >= LOCKOUT_THRESHOLD:
            user.locked_until = datetime.now(timezone.utc) + timedelta(
                minutes=LOCKOUT_DURATION_MINUTES
            )

        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Successful login - reset failed login count and clear lock
    user.failed_login_count = 0
    user.locked_until = None
    db.commit()

    # Create JWT token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}
    )

    return TokenResponse(access_token=access_token)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: UserCreate, db: Session = Depends(get_db)):
    """Register a new user.

    - Checks username uniqueness
    - Validates password complexity (1 upper, 1 lower, 1 digit)
    - Hashes password and creates user record
    """
    # Check username uniqueness
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # Validate password complexity: at least 1 uppercase, 1 lowercase, 1 digit
    password = request.password
    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one uppercase letter",
        )
    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one lowercase letter",
        )
    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one digit",
        )

    # Hash password and create user
    hashed_password = get_password_hash(password)
    new_user = User(
        username=request.username,
        password_hash=hashed_password,
        full_name=request.full_name,
        email=request.email,
        role=request.role,
        is_active=True,
        failed_login_count=0,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/me", response_model=UserResponse)
def get_me(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Get current authenticated user from Bearer token.

    Manually extracts and decodes JWT from Authorization header.
    Will be replaced by dependency injection in task 4.4.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.get("/users", response_model=List[UserResponse])
def list_users(
    current_user: User = Depends(require_role([UserRole.admin])),
    db: Session = Depends(get_db),
):
    """List all users. Admin-only endpoint."""
    users = db.query(User).order_by(User.id).all()
    return users


@router.patch("/users/{user_id}/toggle-active", response_model=UserResponse)
def toggle_user_active(
    user_id: int,
    current_user: User = Depends(require_role([UserRole.admin])),
    db: Session = Depends(get_db),
):
    """Toggle user active status. Admin-only.

    Prevents deactivating the last active admin user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # If deactivating an admin, check that at least one other active admin remains
    if user.is_active and user.role == UserRole.admin:
        active_admin_count = (
            db.query(User)
            .filter(User.role == UserRole.admin, User.is_active == True, User.id != user_id)
            .count()
        )
        if active_admin_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate the last active admin",
            )

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user

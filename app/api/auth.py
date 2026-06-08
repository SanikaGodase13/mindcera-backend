from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.core.dependencies import get_current_user
from app.schemas.user import UserProfile
from app.schemas.user import ForgotPasswordRequest

from app.models.password_reset_otp import PasswordResetOTP
from app.services.otp_service import create_password_reset_otp
from app.services.email_service import send_otp_email

from app.schemas.user import VerifyOTPRequest
from datetime import datetime, timezone
from app.schemas.user import ResetPasswordRequest

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register")
def register_user(
    user: UserRegister,
    db: Session = Depends(get_db)
):
    
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
        age=user.age,
        gender=user.gender,
        occupation=user.occupation,
        mental_health_goal=user.mental_health_goal
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully"
    }


@router.post("/login")
def login_user(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    db_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        user.password,
        db_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        {
            "sub": db_user.email,
            "user_id": db_user.id
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get(
    "/profile",
    response_model=UserProfile
)
def get_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    otp_record = create_password_reset_otp(
        db=db,
        user_id=user.id
    )

    send_otp_email(
        receiver_email=user.email,
        otp=otp_record.otp
    )

    return {
        "message": "OTP sent successfully"
    }


@router.post("/verify-otp")
def verify_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    otp_record = (
        db.query(PasswordResetOTP)
        .filter(
            PasswordResetOTP.user_id == user.id,
            PasswordResetOTP.otp == request.otp,
            PasswordResetOTP.is_used == False
        )
        .order_by(
            PasswordResetOTP.created_at.desc()
        )
        .first()
    )

    if not otp_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    if otp_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400,
            detail="OTP expired"
        )

    return {
        "message": "OTP verified successfully"
    }


@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    otp_record = (
        db.query(PasswordResetOTP)
        .filter(
            PasswordResetOTP.user_id == user.id,
            PasswordResetOTP.otp == request.otp,
            PasswordResetOTP.is_used == False
        )
        .order_by(
            PasswordResetOTP.created_at.desc()
        )
        .first()
    )

    if not otp_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    if otp_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400,
            detail="OTP expired"
        )

    user.password_hash = hash_password(
        request.new_password
    )

    otp_record.is_used = True

    db.commit()

    return {
        "message": "Password reset successfully"
    }
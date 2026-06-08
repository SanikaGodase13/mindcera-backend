from datetime import datetime, timedelta, timezone

from app.core.otp import generate_otp
from app.models.password_reset_otp import PasswordResetOTP


def create_password_reset_otp(
    db,
    user_id: int
):

    otp = generate_otp()

    expires_at = datetime.now(
        timezone.utc
    ) + timedelta(minutes=10)

    otp_record = PasswordResetOTP(
        user_id=user_id,
        otp=otp,
        expires_at=expires_at
    )

    db.add(otp_record)
    db.commit()
    db.refresh(otp_record)

    return otp_record
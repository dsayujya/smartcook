import random
import re
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from app.models.domain import OTPVerification
from app.config import settings

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def is_valid_email(email: str) -> bool:
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def generate_otp_code() -> str:
    return f"{random.randint(100000, 999999)}"

def send_email_otp(recipient_email: str, otp_code: str):
    """Sends OTP via SMTP if configured, otherwise logs to stdout for development."""
    subject = "SmartCook Verification Code"
    body = f"""
    Hello!

    Your SmartCook verification code is: {otp_code}

    This code is valid for 10 minutes. Please do not share this code with anyone.

    Happy Cooking!
    - SmartCook Team
    """

    if settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD:
        try:
            msg = MIMEMultipart()
            msg["From"] = settings.SMTP_USER
            msg["To"] = recipient_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            print(f"[OTP SERVICE] Email sent successfully to {recipient_email}")
        except Exception as e:
            print(f"[OTP SERVICE] Failed to send email via SMTP: {e}")
    else:
        print(f"==================================================")
        print(f"[OTP SERVICE - DEV MOCK] OTP for {recipient_email}: {otp_code}")
        print(f"==================================================")

def create_and_send_otp(db: Session, target: str, otp_type: str = "email_verification") -> str:
    target_clean = target.strip().lower()
    if not is_valid_email(target_clean):
        raise ValueError("Invalid email format for OTP request")

    otp_code = generate_otp_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    # Invalidate previous unexpired OTPs for this target
    db.query(OTPVerification).filter(
        OTPVerification.target == target_clean,
        OTPVerification.otp_type == otp_type,
        OTPVerification.is_used == False
    ).update({"is_used": True})

    otp_record = OTPVerification(
        target=target_clean,
        otp_code=otp_code,
        otp_type=otp_type,
        expires_at=expires_at,
        is_used=False
    )
    db.add(otp_record)
    db.commit()
    db.refresh(otp_record)

    send_email_otp(target_clean, otp_code)
    return otp_code

def verify_otp_code(db: Session, target: str, otp_code: str, otp_type: str = "email_verification") -> bool:
    target_clean = target.strip().lower()
    otp_code_clean = otp_code.strip()

    record = db.query(OTPVerification).filter(
        OTPVerification.target == target_clean,
        OTPVerification.otp_code == otp_code_clean,
        OTPVerification.is_used == False,
        OTPVerification.expires_at >= datetime.utcnow()
    ).first()

    if not record:
        return False

    record.is_used = True
    db.commit()
    return True


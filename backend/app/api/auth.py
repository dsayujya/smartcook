from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.config import settings
from app.models.domain import User
from app.schemas.schemas import (
    User as UserSchema,
    UserRegisterRequest,
    UserLoginRequest,
    RequestOTPRequest,
    VerifyOTPRequest,
    GoogleAuthRequest,
    TokenResponse,
)
from app.services.jwt_utils import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.services.otp_service import (
    is_valid_email,
    create_and_send_otp,
    verify_otp_code,
)
from app.services.google_auth_service import verify_google_id_token

router = APIRouter(prefix="/auth", tags=["auth"])

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token"
        )
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

@router.post("/register", response_model=TokenResponse)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    email_clean = req.email.strip().lower()
    if not is_valid_email(email_clean):
        raise HTTPException(status_code=400, detail="Invalid email address format. A valid email is required.")

    existing_user = db.query(User).filter(User.email == email_clean).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered. Please sign in.")

    hashed_pwd = hash_password(req.password) if req.password else None
    username = email_clean.split("@")[0]

    new_user = User(
        email=email_clean,
        username=username,
        hashed_password=hashed_pwd,
        full_name=req.full_name,
        is_email_verified=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Dispatch initial email verification OTP
    otp_code = create_and_send_otp(db, email_clean, otp_type="email_verification")

    dev_otp = None
    if not (settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD):
        dev_otp = otp_code

    # Issue JWT token
    access_token = create_access_token(data={"sub": str(new_user.id), "email": new_user.email})
    return TokenResponse(access_token=access_token, user=new_user, dev_otp_code=dev_otp)

@router.post("/request-otp")
def request_otp(req: RequestOTPRequest, db: Session = Depends(get_db)):
    target_clean = req.target.strip().lower()
    if not is_valid_email(target_clean):
        raise HTTPException(status_code=400, detail="Invalid email address format.")

    otp_code = create_and_send_otp(db, target_clean, otp_type=req.otp_type or "email_verification")
    dev_otp = None
    if not (settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD):
        dev_otp = otp_code

    return {
        "message": f"Verification code sent to {target_clean}",
        "target": target_clean,
        "otp_type": req.otp_type,
        "dev_otp_code": dev_otp,
    }

@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(req: VerifyOTPRequest, db: Session = Depends(get_db)):
    target_clean = req.target.strip().lower()
    if not is_valid_email(target_clean):
        raise HTTPException(status_code=400, detail="Invalid email address format.")

    is_valid = verify_otp_code(db, target_clean, req.otp_code, otp_type=req.otp_type or "email_verification")

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP code.")

    # Find or create user for this verified email target
    user = db.query(User).filter(User.email == target_clean).first()
    if user:
        user.is_email_verified = True
    else:
        # Create user if logging in via email OTP for the first time
        username = target_clean.split("@")[0]
        user = User(email=target_clean, username=username, is_email_verified=True)
        db.add(user)

    db.commit()
    db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=access_token, user=user)

@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    email_clean = req.email.strip().lower()
    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password.")

    if not user.hashed_password or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password.")

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=access_token, user=user)

@router.post("/google", response_model=TokenResponse)
def google_auth(req: GoogleAuthRequest, db: Session = Depends(get_db)):
    google_data = verify_google_id_token(req.id_token)
    if not google_data:
        raise HTTPException(status_code=400, detail="Invalid or expired Google OAuth ID token.")

    google_id = google_data["google_id"]
    email = google_data["email"].strip().lower()

    user = db.query(User).filter((User.google_id == google_id) | (User.email == email)).first()

    if user:
        user.google_id = google_id
        if google_data.get("avatar_url") and not user.avatar_url:
            user.avatar_url = google_data["avatar_url"]
        if google_data.get("full_name") and not user.full_name:
            user.full_name = google_data["full_name"]
        user.is_email_verified = True
    else:
        username = email.split("@")[0]
        user = User(
            email=email,
            username=username,
            google_id=google_id,
            full_name=google_data.get("full_name"),
            avatar_url=google_data.get("avatar_url"),
            is_email_verified=True,
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=access_token, user=user)

@router.get("/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

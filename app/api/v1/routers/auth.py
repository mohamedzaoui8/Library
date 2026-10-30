import hashlib
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import user_create, user_login
from app.services.email_service import send_verification_email
from app.services.email_verification_service import create_email_verification

router = APIRouter(prefix="/auth", tags=["Authentication"])


COOKIE_NAME = "library_access_token"


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


# ---------------------------VERIFY_EMAIL---------------------------#
@router.post("/verify-email")
async def verify_email(
    data: VerifyEmailRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    token_hash = hashlib.sha256(data.token.encode("utf-8")).hexdigest()

    result = await db.execute(
        select(User).where(User.email_verification_token_hash == token_hash)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    if (
        user.email_verification_expires_at is None
        or user.email_verification_expires_at <= datetime.now(timezone.UTC)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired",
        )

    user.email_verified = True
    user.email_verification_token_hash = None
    user.email_verification_expires_at = None

    await db.commit()

    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(
    data: ResendVerificationRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    email = str(data.email).strip().lower()
    result = await db.execute(
        select(User)
        .where(User.email == email)
        .with_for_update()
    )
    user = result.scalar_one_or_none()

    generic_response = {
        "message": (
            "If the account needs verification, a code will be sent. "
            "If you requested one recently, wait one minute before trying again."
        )
    }

    if user is None or user.email_verified:
        return generic_response

    now = datetime.now(timezone.UTC)
    if (
        user.email_verification_sent_at is not None
        and now - user.email_verification_sent_at < timedelta(minutes=1)
    ):
        return generic_response

    token = await create_email_verification(user, db)
    await send_verification_email(user.email, token)

    return generic_response


# ---------------------------REGISTER---------------------------#


@router.post("/register")
async def register(
    user: user_create,
    db: Annotated[AsyncSession , Depends(get_db)],
):
    email = str(user.email).strip().lower()
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    new_user = User(
        username=user.username,
        email=email,
        hashed_password=hash_password(user.password),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = await create_email_verification(new_user, db)
    await send_verification_email(new_user.email, token)

    return {"message": "Account created. Verify your email to continue."}


# ---------------------------LOGIN---------------------------#
@router.post("/login")
async def login(
    user: user_login, response: Response, db: Annotated[AsyncSession ,Depends(get_db)],
):
    email = str(user.email).strip().lower()
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()
    if (
        existing_user is None
        or existing_user.hashed_password is None
        or not verify_password(user.password, existing_user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(existing_user)
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    return {"message": "Login successful"}


# ---------------------------LOGOUT---------------------------#
@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="library_access_token",
        path="/",
    )
    return {"message": "Logged out successfully"}

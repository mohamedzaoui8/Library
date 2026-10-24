
import hashlib
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.security import hash_password ,verify_password , create_access_token
from app.models.user import User
from app.schemas.user import user_create, user_login

router = APIRouter(prefix="/auth", tags=["Authentication"])



class VerifyEmailRequest(BaseModel):
    token: str



#---------VERIFY_EMAIL---------#
@router.post("/verify-email")
async def verify_email(
    data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    token_hash = hashlib.sha256(
        data.token.encode("utf-8")
    ).hexdigest()

    result = await db.execute(
        select(User).where(
            User.email_verification_token_hash == token_hash
        )
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    if (
        user.email_verification_expires_at is None
        or user.email_verification_expires_at
        <= datetime.now(timezone.utc)
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

#---------REGISTER---------#

@router.post("/register")
async def register(user : user_create ,db :AsyncSession =Depends(get_db),):
    email = str(user.email).strip().lower()
    result =await db.execute(select(User).where(User.email== email))
    existing_user = result.scalar_one_or_none()

    if existing_user is not None :
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    new_user =User(
        username =user.username,
        email=email,
        hashed_password=hash_password(user.password),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "Account created. Verify your email to continue."}

#---------LOGIN---------#
@router.post("/login")
async def login(user :user_login , db:AsyncSession=Depends(get_db))
    email = str(user.email).strip().lower()
    result =await db.execute(select(User).where(User.email== email))
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
    create_access_token(existing_user)


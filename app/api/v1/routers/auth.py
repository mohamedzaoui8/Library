
import hashlib
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.models.user import User

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

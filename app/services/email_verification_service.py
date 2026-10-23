
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


def generate_verification_token() -> tuple[str, str]:
    token = f"{secrets.randbelow(1_000_000):06d}"
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return token, token_hash


def get_verification_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=1)





async def create_email_verification(
    user: User,
    db: AsyncSession,
) -> str:
    token, token_hash = generate_verification_token()

    user.email_verified = False
    user.email_verification_token_hash = token_hash
    user.email_verification_expires_at = get_verification_expiry()

    await db.commit()
    await db.refresh(user)

    return token

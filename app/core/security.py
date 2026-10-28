from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select

from app.core.config import settings
from app.models.user import User

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(user: User) -> str:
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive.",
        )
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in.",
        )

    expire = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user.id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise ValueError("Invalid token")

        return int(user_id)

    except (InvalidTokenError, ValueError) as exc:
        raise ValueError("Invalid token") from exc

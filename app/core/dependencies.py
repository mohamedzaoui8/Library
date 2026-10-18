from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = decode_access_token(token)
    except ValueError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise credentials_exception

    return user


def require_admin(
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permissions are required.",
        )

    return current_user


def require_member(
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="member access required",
        )
    if not current_user.is_active:
        raise HTTPException(
            status_code=401,
            detail="member has been deleted"
        )

    return current_user

def require_admin_or_user(
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "member"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this page."
        )
    if not current_user.is_active:
        raise HTTPException(
            status_code=401,
            detail="member has been deleted"
        )

    return current_user
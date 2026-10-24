from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.user import User


async def authenticate_google_user(
    db: AsyncSession,
    google_sub: str,
    email: str,
    name: str | None = None,
) -> str:
    # 1. Search for the user by Google ID
    result = await db.execute(select(User).where(User.google_sub == google_sub))
    user = result.scalar_one_or_none()

    # 2. Create the user if they do not exist
    if user is None:
        user = User(
            google_sub=google_sub,
            email=email,
            username=name,
            hashed_password=None,
            email_verified=True,
            # Add your other required fields here
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
    # 3. Reject inactive accounts
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive.",
        )

    # 3. Generate the Library JWT
    return create_access_token(user.id)

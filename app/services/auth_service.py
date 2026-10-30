from fastapi import HTTPException, status
from sqlalchemy import IntegrityError, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.user import User


async def make_unique_username(db: AsyncSession, name: str | None, email: str) -> str:
    base = (name or email.split("@", 1)[0]).strip()
    if not base:
        base = "reader"

    base = base[:240]
    username = base
    suffix = 1

    while True:
        result = await db.execute(select(User.id).where(User.username == username))
        if result.scalar_one_or_none() is None:
            return username

        username = f"{base[:230]}_{suffix}"
        suffix += 1

async def authenticate_google_user(
    db: AsyncSession,
    google_sub: str,
    email: str,
    name: str | None = None,
    google_email_verified: bool = False,
) -> str:

    email = email.strip().lower()

    # 1. التأكد من أن Google وثّق البريد.
    if not google_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Google email is not verified.",
        )

    # 2. البحث باستخدام Google Sub.
    result = await db.execute(
        select(User).where(User.google_sub == google_sub)
    )
    user = result.scalar_one_or_none()

    # 3. إذا وجدنا المستخدم، نتحقق من نشاط الحساب.
    if user is not None:

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account is inactive.",
            )

        return create_access_token(user)

    # 4. لم نجد Google Sub، نبحث باستخدام البريد.
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    # 5. البريد موجود في Library، لكن الحساب غير مرتبط بـ Google.
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An account with this email already exists. "
                "Please sign in using your existing Library credentials "
                "and link your Google account from account settings."
            ),
        )

    # 6. لا يوجد حساب بهذا البريد، ننشئ حساباً جديداً.
    username = await make_unique_username(db, name, email)

    user = User(
        google_sub=google_sub,
        email=email,
        username=username,
        hashed_password=None,
        email_verified=True,
    )

    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)

    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create this Google account.",
        ) from None

    # 7. التحقق من حالة الحساب.
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive.",
        )

    return create_access_token(user)
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_admin
from app.models.book import Book
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=list[CategoryResponse])
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    category = await db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    data: CategoryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin=Depends(require_admin),# noqa: B008
):
    category = Category(**data.model_dump())
    db.add(category)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A category with this name already exists.",
        ) from None

    await db.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin=Depends(require_admin),# noqa: B008
):
    category = await db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    if not changes:
        raise HTTPException(status_code=400, detail="No changes provided")

    for field, value in changes.items():
        setattr(category, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A category with this name already exists.",
        ) from None

    await db.refresh(category)
    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    category_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin=Depends(require_admin), # noqa: B008
):
    category = await db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    result = await db.execute(
        select(Book.id).where(Book.category_id == category_id).limit(1)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete a category that has books.",
        )

    await db.delete(category)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
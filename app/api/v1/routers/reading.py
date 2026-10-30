from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_db, require_admin_or_member
from app.models.book import Book
from app.models.reading_list_Item import ReadingListItem
from app.models.reading_progress import ReadingProgress
from app.models.user import User

#--------------------------------------------------------------------
#from app.schemas.book import BookResponse   ***BACK_TO_IT***
#--------------------------------------------------------------------
from app.schemas.reading_list_item import (
    ReadingListItemCreate,
    ReadingListItemResponse,
)
from app.schemas.reading_progress import (
    ReadingProgressResponse,
    ReadingProgressUpdate,
)

router = APIRouter(tags=["Reading"])


def book_loading_options():
    return (
        selectinload(ReadingListItem.book_rel).selectinload(Book.author_rel),
        selectinload(ReadingListItem.book_rel).selectinload(Book.category_rel),
    )


@router.get(
    "/reading-list",
    response_model=list[ReadingListItemResponse],
)
async def get_reading_list(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_member)],
):
    result = await db.execute(
        select(ReadingListItem)
        .options(*book_loading_options())
        .where(ReadingListItem.user_id == current_user.id)
        .order_by(ReadingListItem.id.desc())
    )
    return result.scalars().all()


@router.post(
    "/reading-list",
    response_model=ReadingListItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_to_reading_list(
    data: ReadingListItemCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_member)],
):
    if await db.get(Book, data.book_id) is None:
        raise HTTPException(status_code=404, detail="Book not found")

    result = await db.execute(
        select(ReadingListItem).where(
            ReadingListItem.user_id == current_user.id,
            ReadingListItem.book_id == data.book_id,
        )
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=409,
            detail="This book is already in your reading list.",
        )

    item = ReadingListItem(
        user_id=current_user.id,
        book_id=data.book_id,
    )
    db.add(item)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This book is already in your reading list.",
        ) from None

    result = await db.execute(
        select(ReadingListItem)
        .options(*book_loading_options())
        .where(ReadingListItem.id == item.id)
    )
    return result.scalar_one()


@router.delete(
    "/reading-list/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_from_reading_list(
    book_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_member)],
):
    result = await db.execute(
        select(ReadingListItem).where(
            ReadingListItem.user_id == current_user.id,
            ReadingListItem.book_id == book_id,
        )
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book is not in your list"
        )

    await db.delete(item)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/reading-progress/{book_id}",
    response_model=ReadingProgressResponse,
)
async def get_reading_progress(
    book_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_member)],
):
    if await db.get(Book, book_id) is None:
        raise HTTPException(status_code=404, detail="Book not found")

    result = await db.execute(
        select(ReadingProgress).where(
            ReadingProgress.user_id == current_user.id,
            ReadingProgress.book_id == book_id,
        )
    )
    progress = result.scalar_one_or_none()

    if progress is None:
        return ReadingProgressResponse(
            book_id=book_id,
            progress_percentage=0,
        )
    return progress


@router.put(
    "/reading-progress/{book_id}",
    response_model=ReadingProgressResponse,
)
async def save_reading_progress(
    book_id: int,
    data: ReadingProgressUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_member)],
):
    if await db.get(Book, book_id) is None:
        raise HTTPException(status_code=404, detail="Book not found")

    result = await db.execute(
        select(ReadingProgress).where(
            ReadingProgress.user_id == current_user.id,
            ReadingProgress.book_id == book_id,
        )
    )
    progress = result.scalar_one_or_none()

    if progress is None:
        progress = ReadingProgress(
            user_id=current_user.id,
            book_id=book_id,
            progress_percentage=data.progress_percentage,
        )
        db.add(progress)
    else:
        progress.progress_percentage = data.progress_percentage

    await db.commit()
    await db.refresh(progress)
    return progress


@router.delete(
    "/reading-progress/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_reading_progress(
    book_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_member)],
):
    result = await db.execute(
        select(ReadingProgress).where(
            ReadingProgress.user_id == current_user.id,
            ReadingProgress.book_id == book_id,
        )
    )
    progress = result.scalar_one_or_none()
    if progress is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reading progress not found"
        )

    await db.delete(progress)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

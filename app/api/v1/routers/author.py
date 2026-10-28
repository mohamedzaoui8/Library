from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_admin
from app.models.author import Author
from app.models.book import Book
from app.schemas.author import AuthorCreate, AuthorResponse, AuthorUpdate

router = APIRouter(prefix="/authors", tags=["Authors"])


@router.get("/", response_model=list[AuthorResponse])
async def list_authors(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Author).order_by(Author.lastname, Author.firstname)
    )
    return result.scalars().all()


@router.get("/{author_id}", response_model=AuthorResponse)
async def get_author(
    author_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    author = await db.get(Author, author_id)
    if author is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    return author


@router.post(
    "/",
    response_model=AuthorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_author(
    data: AuthorCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin=Depends(require_admin), # noqa: B008
):
    author = Author(**data.model_dump())
    db.add(author)
    await db.commit()
    await db.refresh(author)
    return author


@router.patch("/{author_id}", response_model=AuthorResponse)
async def update_author(
    author_id: int,
    data: AuthorUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin=Depends(require_admin), # noqa: B008
):
    author = await db.get(Author, author_id)
    if author is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")

    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    if not changes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No changes provided")

    for field, value in changes.items():
        setattr(author, field, value)

    await db.commit()
    await db.refresh(author)
    return author


@router.delete(
    "/{author_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_author(
    author_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin=Depends(require_admin), # noqa: B008
):
    author = await db.get(Author, author_id)
    if author is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")

    result = await db.execute(
        select(Book.id).where(Book.author_id == author_id).limit(1)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete an author who has books.",
        )

    await db.delete(author)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
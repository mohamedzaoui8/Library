from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_db, require_admin, require_admin_or_member
from app.models.author import Author
from app.models.book import Book
from app.models.book_file import BookFile
from app.models.category import Category
from app.models.user import User
from app.schemas.book import BookCreate, BookResponse, BookUpdate
from app.schemas.book_file import BookFileResponse

router = APIRouter(prefix="/books", tags=["Books"])

# books.py موجود في app/api/v1/routers؛ parents[4] هو مجلد المشروع.
STORAGE_DIR = Path(__file__).resolve().parents[4] / "storage" / "books"
MAX_FILE_SIZE = 100 * 1024 * 1024


async def load_book(db: AsyncSession, book_id: int) -> Book:
    result = await db.execute(
        select(Book)
        .options(
            selectinload(Book.author_rel),
            selectinload(Book.category_rel),
        )
        .where(Book.id == book_id)
    )
    book = result.scalar_one_or_none()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.get("/", response_model=list[BookResponse])
async def list_books(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str | None = Query(default=None, min_length=1),
    author_id: int | None = None,
    category_id: int | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    query = select(Book).options(
        selectinload(Book.author_rel),
        selectinload(Book.category_rel),
    )

    if author_id is not None:
        query = query.where(Book.author_id == author_id)

    if category_id is not None:
        query = query.where(Book.category_id == category_id)

    if q:
        search = f"%{q.strip()}%"
        query = query.join(Book.author_rel).where(
            or_(
                Book.title.ilike(search),
                Author.firstname.ilike(search),
                Author.lastname.ilike(search),
            )
        )

    query = query.order_by(Book.title).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await load_book(db, book_id)


@router.post(
    "/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_book(
    data: BookCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin=Depends(require_admin),#noqa :B008
):
    if await db.get(Author, data.author_id) is None:
        raise HTTPException(status_code=404, detail="Author not found")

    if await db.get(Category, data.category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")

    book = Book(**data.model_dump())
    db.add(book)
    await db.commit()
    return await load_book(db, book.id)


@router.patch("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    data: BookUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin=Depends(require_admin), #noqa :B008
):
    book = await db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    if not changes:
        raise HTTPException(status_code=400, detail="No changes provided")

    if "author_id" in changes and await db.get(Author, changes["author_id"]) is None:
        raise HTTPException(status_code=404, detail="Author not found")

    if (
        "category_id" in changes
        and await db.get(Category, changes["category_id"]) is None
    ):
        raise HTTPException(status_code=404, detail="Category not found")

    for field, value in changes.items():
        setattr(book, field, value)

    await db.commit()
    return await load_book(db, book_id)


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_book(
    book_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin=Depends(require_admin),#noqa :B008
):
    result = await db.execute(
        select(Book)
        .options(selectinload(Book.files))
        .where(Book.id == book_id)
    )
    book = result.scalar_one_or_none()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    paths = [Path(book_file.file_path) for book_file in book.files]

    await db.delete(book)
    await db.commit()

    # حذف الملفات الفعلية من القرص بعد حذف سجلاتها من قاعدة البيانات.
    for path in paths:
        path.unlink(missing_ok=True)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{book_id}/files",
    response_model=list[BookFileResponse],
)
async def list_book_files(
    book_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await load_book(db, book_id)
    result = await db.execute(
        select(BookFile)
        .where(BookFile.book_id == book_id)
        .order_by(BookFile.created_at)
    )
    return result.scalars().all()


@router.post(
    "/{book_id}/files",
    response_model=BookFileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_book_file(
    book_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin=Depends(require_admin),#noqa :B008
    file: UploadFile = File(...),#noqa :B008
):
    await load_book(db, book_id)

    original_name = Path(file.filename or "upload").name
    extension = Path(original_name).suffix.lower()

    if extension not in {".pdf", ".epub"}:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and EPUB files are supported.",
        )

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex}{extension}"
    destination = STORAGE_DIR / stored_name
    file_size = 0

    try:
        with destination.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File exceeds the 100 MB limit.",
                    )
                output.write(chunk)

        if file_size == 0:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")

        book_file = BookFile(
            book_id=book_id,
            file_name=stored_name,
            original_name=original_name[:255],
            file_path=str(destination),
            file_format=extension.removeprefix("."),
            file_size=file_size,
            processing_status="pending",
        )
        db.add(book_file)
        await db.commit()
        await db.refresh(book_file)
        return book_file

    except Exception:
        await db.rollback()
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()


@router.get(
    "/{book_id}/files/{file_id}/download",
    response_class=FileResponse,
)
async def download_book_file(
    book_id: int,
    file_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_member)],
):
    result = await db.execute(
        select(BookFile).where(
            BookFile.id == file_id,
            BookFile.book_id == book_id,
        )
    )
    book_file = result.scalar_one_or_none()
    if book_file is None:
        raise HTTPException(status_code=404, detail="Book file not found")

    path = Path(book_file.file_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Stored file not found")

    media_type = (
        "application/pdf"
        if book_file.file_format == "pdf"
        else "application/epub+zip"
    )
    return FileResponse(
        path=path,
        media_type=media_type,
        filename=book_file.original_name,
    )


@router.delete(
    "/{book_id}/files/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_book_file(
    book_id: int,
    file_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin=Depends(require_admin),#noqa :B008
):
    result = await db.execute(
        select(BookFile).where(
            BookFile.id == file_id,
            BookFile.book_id == book_id,
        )
    )
    book_file = result.scalar_one_or_none()
    if book_file is None:
        raise HTTPException(status_code=404, detail="Book file not found")

    path = Path(book_file.file_path)
    await db.delete(book_file)
    await db.commit()
    path.unlink(missing_ok=True)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
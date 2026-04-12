import fitz
import uuid
from app.repositories.document_repository import create_document_from_files
from fastapi import UploadFile
from app.models.document import Document
from sqlalchemy.orm import Session


UPLOAD_DIR = "uploads/"

async def ingest_pdf(
    db: Session,
    user_id: str,
    title: str,
    file: UploadFile,
) -> Document:
    # 1. save raw file to disk
    file_name = file.filename
    file_path = f"{UPLOAD_DIR}{uuid.uuid4()}_{file_name}"
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # 2. extract text
    pdf = fitz.open(file_path)
    raw_content = "\n".join(page.get_text() for page in pdf)

    # 3. store in db
    document = create_document_from_files(
        db=db,
        user_id=user_id,
        title=title,
        raw_content=raw_content,
        file_name=file_name,
        file_size=len(content),
        mime_type="application/pdf",
        file_path=file_path,
    )

    return document
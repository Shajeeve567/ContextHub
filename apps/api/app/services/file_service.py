import uuid
from app.repositories.document_repository import create_document_from_files
from fastapi import UploadFile
from app.models.document import Document
from sqlalchemy.orm import Session
import shutil
from langchain_community.document_loaders import PyPDFLoader
import os

UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def ingest_pdf(
    db: Session,
    user_id: str,
    title: str,
    file: UploadFile,
) -> Document:
    # 1. save raw file to disk
    file_name = file.filename
    file_path = f"{UPLOAD_DIR}{uuid.uuid4()}_{file_name}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. get file size from saved file
    file_size = os.path.getsize(file_path)

    # 3. extract text
    loader = PyPDFLoader(file_path)
    raw_content = "\n".join([doc.page_content for doc in loader.load()])

    # 4. store in db
    document = create_document_from_files(
        db=db,
        user_id=user_id,
        title=title,
        raw_content=raw_content,
        file_name=file_name,
        file_size=file_size,
        mime_type="application/pdf",
        file_path=file_path,
    )

    return document
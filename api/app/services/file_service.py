import asyncio
import uuid

from api.app.repositories.document_repository import create_document_from_files
from fastapi import UploadFile
from api.app.models.document import Document
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_community.document_loaders import PyPDFLoader
import os

UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def _store_and_extract_pdf(file_bytes: bytes, file_path: str) -> tuple[int, str]:
    with open(file_path, "wb") as buffer:
        buffer.write(file_bytes)

    file_size = os.path.getsize(file_path)
    loader = PyPDFLoader(file_path)
    raw_content = "\n".join([doc.page_content for doc in loader.load()])
    return file_size, raw_content


async def ingest_pdf(
    db: AsyncSession,
    user_id: str,
    title: str,
    file: UploadFile,
) -> Document:
    file_name = file.filename
    file_path = f"{UPLOAD_DIR}{uuid.uuid4()}_{file_name}"

    file_bytes = await file.read()
    file_size, raw_content = await asyncio.to_thread(_store_and_extract_pdf, file_bytes, file_path)

    document = await create_document_from_files(
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
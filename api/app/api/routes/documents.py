from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from api.app.core.database import get_db
from api.app.repositories.document_repository import (
    create_document,
    get_document_by_id,
    list_documents_for_user,
)
from api.app.schemas.document import DocumentCreate, DocumentProcessResponse, DocumentResponse, DocumentCreateFromFile
from api.app.services.ingestion_service import process_document
from api.app.services.file_service import ingest_pdf

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document_endpoint(payload: DocumentCreate, db: AsyncSession = Depends(get_db)):
    document = await create_document(db, payload)
    return document

@router.post("/upload-pdf", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf_endpoint(
    user_id: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    document = await ingest_pdf(db=db, user_id=user_id, title=title, file=file)
    return document

@router.get("", response_model=List[DocumentResponse])
async def list_documents_endpoint(
    user_id: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    return await list_documents_for_user(db, user_id)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_endpoint(
    document_id: str,
    user_id: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    document = await get_document_by_id(db, document_id=document_id, user_id=user_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/{document_id}/process", response_model=DocumentProcessResponse)
async def process_document_endpoint(
    document_id: str,
    user_id: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    document = await get_document_by_id(db, document_id=document_id, user_id=user_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    stored_chunks = await process_document(db, document)

    return DocumentProcessResponse(
        document_id=document.id,
        chunks_created=len(stored_chunks),
        status="processed",
    )
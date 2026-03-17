from sqlalchemy.orm import Session

from app.models.document import Document
from app.repositories.chunk_repository import replace_chunks_for_document
from app.repositories.document_repository import update_document_status
from app.services.chunking_service import split_text_into_chunks
from app.services.embedding_service import embed_texts


def process_document(db: Session, document: Document):
    chunk_dicts = split_text_into_chunks(document.raw_content)

    if not chunk_dicts:
        update_document_status(db, document, "processed")
        return []

    chunk_texts = [chunk["chunk_text"] for chunk in chunk_dicts]
    embeddings = embed_texts(chunk_texts)

    payloads = []
    for chunk_dict, embedding in zip(chunk_dicts, embeddings):
        payloads.append(
            {
                "chunk_index": chunk_dict["chunk_index"],
                "chunk_text": chunk_dict["chunk_text"],
                "token_count": chunk_dict["token_count"],
                "embedding": embedding,
                "meta_json": chunk_dict["meta_json"],
            }
        )

    stored_chunks = replace_chunks_for_document(db, document.id, payloads)
    update_document_status(db, document, "processed")

    return stored_chunks
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from api.app.models.document import Document
from api.app.repositories.chunk_repository import replace_chunks_for_document
from api.app.repositories.document_repository import update_document_status
from api.app.services.chunking_service import SemanticChunker
from api.app.services.embedding_service import STMEmbedding


async def process_document(db: AsyncSession, document: Document):
    chunker = SemanticChunker()
    embedder = STMEmbedding()

    chunk_dicts = await asyncio.to_thread(chunker.semantic_chunking, document.raw_content)

    if not chunk_dicts:
        await update_document_status(db, document, "processed")
        return []

    chunk_texts = [chunk["chunk_text"] for chunk in chunk_dicts]
    embeddings = await asyncio.to_thread(embedder.embed_documents, chunk_texts)

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

    stored_chunks = await replace_chunks_for_document(db, document.id, payloads)
    await update_document_status(db, document, "processed")

    return stored_chunks
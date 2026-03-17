from typing import List

from app.core.config import settings
from app.utils.text import estimate_token_count, sanitize_text


def split_text_into_chunks(
    text: str,
    chunk_size: int = settings.CHUNK_SIZE,
    overlap: int = settings.CHUNK_OVERLAP,
) -> List[dict]:
    cleaned = sanitize_text(text)
    if not cleaned:
        return []

    chunks: List[dict] = []
    start = 0
    chunk_index = 0
    text_length = len(cleaned)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        piece = cleaned[start:end]

        # Try not to cut mid-word when possible
        if end < text_length:
            last_space = piece.rfind(" ")
            if last_space > int(chunk_size * 0.6):
                end = start + last_space
                piece = cleaned[start:end]

        piece = piece.strip()
        if piece:
            chunks.append(
                {
                    "chunk_index": chunk_index,
                    "chunk_text": piece,
                    "token_count": estimate_token_count(piece),
                    "meta_json": {
                        "start_char": start,
                        "end_char": end,
                    },
                }
            )
            chunk_index += 1

        if end >= text_length:
            break

        start = max(0, end - overlap)

    return chunks
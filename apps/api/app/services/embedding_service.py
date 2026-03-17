import hashlib
import math
import re
from typing import List

# Starter-only embedding approach:
# This is NOT a true semantic embedding model.
# It gives you a deterministic vector so the architecture works now.
# Later you can replace this file with a real embedding provider.

VECTOR_SIZE = 256


def _tokenize(text: str) -> List[str]:
    return re.findall(r"\b\w+\b", text.lower())


def embed_text(text: str, dimensions: int = VECTOR_SIZE) -> List[float]:
    vector = [0.0] * dimensions
    tokens = _tokenize(text)

    if not tokens:
        return vector

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()

        bucket = int(digest[:8], 16) % dimensions
        sign = -1.0 if int(digest[8:10], 16) % 2 else 1.0

        vector[bucket] += sign

    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def embed_texts(texts: List[str], dimensions: int = VECTOR_SIZE) -> List[List[float]]:
    return [embed_text(text, dimensions=dimensions) for text in texts]
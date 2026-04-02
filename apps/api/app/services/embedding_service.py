from typing import List
from app.services.embedding_models import embedding_model
from langchain_core.embeddings import Embeddings
import numpy as np


class STMEmbedding(Embeddings):
    def __init__(
            self,
            normalize: bool = True,
            batch_size: int = 32
    ):
        self.model = embedding_model
        self.normalize = normalize
        self.batch_size = batch_size

    def embed_texts(self, texts: List[str]):
        return self.model.encode(
            texts,
            batch_size=self.batch_size,
            convert_to_numpy=True,
            show_progress_bar=True,
            normalize_embeddings=self.normalize
        ).astype(np.float32).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=self.normalize,
        ).astype(np.float32).tolist()
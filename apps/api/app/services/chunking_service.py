from typing import List
import re
from app.core.config import settings
from app.utils.text import estimate_token_count, sanitize_text
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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


class SemanticChunker:
    def __init__(self, model_name="all-MiniLM-L6-v2", threshold_percentile=95):
        self.model = SentenceTransformer(model_name)
        self.threshold_percentile = threshold_percentile 
    
    def combine_sentences(self, sentences, buffer_size=1):
        for i in range(len(sentences)):
            combined_sentence = ''

            for j in range(i-buffer_size, i):
                if j >= 0:
                    combined_sentence += sentences[j]["sentence"] + " "

            combined_sentence += sentences[i]["sentence"]

            for j in range(i+1, i + 1 + buffer_size):
                if j < len(sentences):
                    combined_sentence += " " + sentences[j]["sentence"]
        return sentences
    
    def get_embedding(self, sentences):
        only_combined_sentences = [i["combined_sentence"] for i in sentences]
        return self.model.encode(only_combined_sentences, show_progress_bar=True)
        
    def calculate_cosine_distances(self, sentences):
        distances = []

        embeddings = self.get_embedding(sentences)
        for i, sentence in enumerate(sentences):
            sentence["combined_sentence_embedding"] = embeddings[i]
        
        for i in range(len(sentences) - 1):
            embedding_current = sentences[i]["combined_sentence_embedding"]
            embedding_next = sentences[i+1]["combined_sentence_embedding"]

            similarity = cosine_similarity(embedding_current, embedding_next)
            distance = 1 - similarity

            distances.append(distance)

            sentences[i]["distance_to_next"] = distance

        return distances, sentences
    
    def create_chunks(self, sentences, distances):
        breakpoint_distance_threshold = np.percentile(distances, self.threshold_percentile)

        # storing the index of distances larger than threshold
        indices_above_thresh = [i for i, x in enumerate(distances) if x > breakpoint_distance_threshold]

        start_index = 0
        chunks = []
        for index in indices_above_thresh:
            end_index = index

            group = sentences[start_index:end_index + 1]
            combined_text = " ".join(d["sentence"] for d in group)
            chunks.append(combined_text)

            start_index += 1

        if(start_index < len(sentences)):
            combined_text = ' '.join([d['sentence'] for d in sentences[start_index:]])
            chunks.append(combined_text)

        return chunks
    
    def semantic_chunking(self, text: str):
        single_sentences_list = re.split(r'(?<=[.?!])\s', text)
        sentences = [
            {'sentence': x, 'index': i} for i, x in enumerate(single_sentences_list)
        ]
        sentences = self.combine_sentences(sentences=sentences)
        distances, sentences = self.calculate_cosine_distances(sentences)

        return self.create_chunks(sentences, distances)



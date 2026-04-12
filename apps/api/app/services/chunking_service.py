from typing import List
import re
from app.core.config import settings
from app.utils.text import estimate_token_count, sanitize_text
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.core.embedding_models import embedding_model


class SemanticChunker:
    def __init__(self, threshold_percentile=95):
        self.model = embedding_model
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
        
            sentences[i]["combined_sentence"] = combined_sentence

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

            similarity = cosine_similarity([embedding_current], [embedding_next])[0][0]
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
    
    def semantic_chunking(self, text: str) -> List[dict]:
        single_sentences_list = re.split(r'(?<=[.?!])\s', text)
        sentences = [
            {'sentence': x, 'index': i} for i, x in enumerate(single_sentences_list)
        ]
        sentences = self.combine_sentences(sentences=sentences)
        distances, sentences = self.calculate_cosine_distances(sentences)

        chunks = self.create_chunks(sentences, distances)
        
        # Convert to dict format like normal chunking
        chunk_dicts = []
        for chunk_index, chunk_text in enumerate(chunks):
            chunk_dicts.append({
                "chunk_index": chunk_index,
                "chunk_text": chunk_text,
                "token_count": estimate_token_count(chunk_text),
                "meta_json": {
                    "method": "semantic",
                    # No start/end char for semantic chunking
                },
            })
        
        return chunk_dicts



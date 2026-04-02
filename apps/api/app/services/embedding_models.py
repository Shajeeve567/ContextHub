from sentence_transformers import SentenceTransformer

# Initialize once at module load
embedding_model = SentenceTransformer("all-MiniLM-L6-v2") 
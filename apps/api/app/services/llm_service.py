from typing import List
from openai import OpenAI
from app.core.config import settings


client = OpenAI(
    api_key=settings.OPENROUTER_API_KEY.get_secret_value(),
    base_url="https://openrouter.ai/api/v1",
)


def generate_grounded_answer(question: str, retrieval_results: List[dict]) -> str:
    if not retrieval_results:
        return "I could not find anything relevant in your saved knowledge yet."

    # Build context block from retrieved chunks
    context_blocks = []
    for idx, result in enumerate(retrieval_results[:5], start=1):
        title = result["document_title"]
        text = result["chunk"].chunk_text.strip()
        context_blocks.append(f"[{idx}] From '{title}':\n{text}")

    context = "\n\n".join(context_blocks)

    system_prompt = """You are a helpful assistant with access to the user's personal knowledge base.
Your job is to answer the user's question using only the context provided.
If the context does not contain enough information to answer, say so honestly.
Do not make up information that is not in the context."""

    user_prompt = f"""Context from knowledge base:

{context}

Question: {question}

Answer based on the context above:"""

    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content
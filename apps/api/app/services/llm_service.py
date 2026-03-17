from typing import List


def generate_grounded_answer(question: str, retrieval_results: List[dict]) -> str:
    if not retrieval_results:
        return "I could not find anything relevant in your saved memory yet."

    lines = [f"Here is what I found in your saved knowledge about: {question}", ""]

    for idx, result in enumerate(retrieval_results[:3], start=1):
        title = result["document_title"]
        text = result["chunk"].chunk_text.strip()
        lines.append(f"{idx}. From '{title}': {text}")

    lines.append("")
    lines.append("This is a grounded answer built from retrieved chunks. Later you can replace this with a real LLM response.")

    return "\n".join(lines)
from typing import List
from openai import OpenAI
from api.app.core.config import settings
from app.services.prompt_service import build_grounded_answer_prompt, build_context_handoff_prompt

client = OpenAI(
    api_key=settings.OPENROUTER_API_KEY.get_secret_value(),
    base_url="https://openrouter.ai/api/v1",
)

def call_llm(system_prompt: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


# input is dict comes from route endpoint
def generate_context_handoff(context: dict) -> str:
    system_prompt, user_prompt = build_context_handoff_prompt(context)
    return call_llm(system_prompt, user_prompt)



def generate_grounded_answer(question: str, retrieval_results: List[dict]) -> str:
    if not retrieval_results:
        return "I could not find anything relevant in your saved knowledge yet."

    system_prompt, user_prompt = build_grounded_answer_prompt(question, retrieval_results)
    return call_llm(system_prompt, user_prompt)

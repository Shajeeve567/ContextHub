from typing import List
from fastapi import HTTPException, status
from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    RateLimitError,
)
from api.app.core.config import settings
from api.app.services.prompt_service import build_grounded_answer_prompt, build_context_handoff_prompt

client = OpenAI(
    api_key=settings.OPENROUTER_API_KEY.get_secret_value(),
    base_url="https://openrouter.ai/api/v1",
)

def call_llm(system_prompt: str, user_prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content
    except RateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="The LLM provider rate limit was reached. Please retry in a few seconds.",
        ) from exc
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="LLM authentication failed. Check OPENROUTER_API_KEY in your environment.",
        ) from exc
    except BadRequestError as exc:
        message = str(exc)
        if "No models provided" in message:
            message = (
                "LLM request was rejected because no model was configured. "
                "Set MODEL_NAME in .env (for example: MODEL_NAME=openrouter/free)."
            )
        else:
            message = f"LLM request was rejected by provider: {message}"

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from exc
    except (APITimeoutError, APIConnectionError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not reach the LLM provider right now. Please try again shortly.",
        ) from exc
    except APIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM provider error: {exc}",
        ) from exc


# input is dict comes from route endpoint
def generate_context_handoff(context: dict) -> str:
    system_prompt, user_prompt = build_context_handoff_prompt(context)
    return call_llm(system_prompt, user_prompt)



def generate_grounded_answer(question: str, retrieval_results: List[dict]) -> str:
    if not retrieval_results:
        return "I could not find anything relevant in your saved knowledge yet."

    system_prompt, user_prompt = build_grounded_answer_prompt(question, retrieval_results)
    return call_llm(system_prompt, user_prompt)

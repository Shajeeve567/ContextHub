from typing import List


GROUNDED_ANSWER_SYSTEM_PROMPT = """You are a helpful assistant with access to the user's personal knowledge base.
Your job is to answer the user's question using only the context provided.
If the context does not contain enough information to answer, say so honestly.
Do not make up information that is not in the context."""


CONTEXT_HANDOFF_SYSTEM_PROMPT = """You are an AI assistant resuming work on a user's project.
You have been provided with the full project context including what was previously worked on, decisions made, and what is pending.
Your job is to continue the user's work seamlessly.
Do not ask the user to re-explain anything already covered in the context.
Greet the user and briefly summarize where things stand."""


def build_grounded_answer_prompt(question: str, retrieval_results: List[dict]) -> tuple[str, str]:
    context_blocks = []
    for idx, result in enumerate(retrieval_results[:5], start=1):
        title = result["document_title"]
        text = result["chunk"].chunk_text.strip()
        context_blocks.append(f"[{idx}] From '{title}':\n{text}")

    context = "\n\n".join(context_blocks)

    user_prompt = f"""Context from knowledge base:

{context}

Question: {question}

Answer based on the context above:"""

    return GROUNDED_ANSWER_SYSTEM_PROMPT, user_prompt


def build_context_handoff_prompt(context: dict) -> tuple[str, str]:
    project = context["project"]
    last_session = context["last_session"]

    incomplete_warning = (
        f"WARNING: There are {context['incomplete_session_count']} incomplete sessions that were interrupted.\n"
        if context["incomplete_sessions"]
        else ""
    )

    if last_session:
        blockers = ", ".join(last_session["blockers"]) if last_session["blockers"] else "None"
        decisions = ", ".join(last_session["decisions"]) if last_session["decisions"] else "None"
        pending = ", ".join(last_session["pending"]) if last_session["pending"] else "None"

        last_session_block = f"""Last Session Summary:
Worked on: {last_session["worked_on"]}
Progress: {last_session["progress"]}
Decisions made: {decisions}
Still pending: {pending}
Blockers: {blockers}
Most important thing to know: {last_session["next_session_briefing"]}"""
    else:
        last_session_block = "No previous sessions. This is the first session for this project."

    user_prompt = f"""Project: {project["name"]}
Description: {project["description"]}
Current Goal: {project["current_goal"]}

{incomplete_warning}{last_session_block}"""

    return CONTEXT_HANDOFF_SYSTEM_PROMPT, user_prompt
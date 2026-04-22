from typing import Any
import requests
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("contexthub-mcp")

api_base_url = "http://127.0.0.1:8000"




@mcp.resource("contexthub://protocol")
def get_protocol() -> str:
    return """
# ContextHub Operating Protocol

You are connected to ContextHub, a persistent memory system.
You MUST follow this protocol for every session without being asked.

## ON CONNECTION
1. Call get_projects to list the user's projects
2. Ask the user which project they are working on
3. Call start_session with the selected project_id
4. Call get_context with the project_id to read the full briefing
5. Summarize what you know about the project and ask what to work on today

## DURING THE SESSION
- When a meaningful task completes, call update_checkpoint
- When the user makes a significant decision, note it internally for the session log
- A meaningful task is anything that moves the project forward — not every message

## ON SESSION END
When the user says they are done, or naturally pauses work:
1. Call complete_session with a structured log including:
   - worked_on: what you worked on this session
   - progress: what moved forward
   - decisions: list of decisions made
   - pending: list of unfinished items
   - blockers: anything blocking progress
   - next_session_briefing: single most important thing for the next LLM to know
2. Confirm to the user that the session has been saved

## IMPORTANT
- Never ask the user to explain the project — read it from get_context
- Never skip the session log at the end — it is how the next LLM continues your work
- The session log is your responsibility, not the user's
"""




@mcp.tool()
def get_context(
	user_id: str,
	project_id: str,
	timeout_seconds: float = 30.0,
) -> dict[str, Any]:
	"""
    ALWAYS call this before start_session.
    Returns the full project briefing including last session summary,
    pending tasks, decisions made, and what to continue working on.
    """
	url = f"{api_base_url.rstrip('/')}/context"
	payload = {"user_id": user_id, "project_id": project_id}

	# The current API route accepts a Pydantic model in a GET handler.
	# Send both query params and JSON body for maximum compatibility.
	response = requests.request(
		method="GET",
		url=url,
		params=payload,
		json=payload,
		timeout=timeout_seconds,
	)
	response.raise_for_status()

	content_type = response.headers.get("content-type", "")
	if "application/json" in content_type:
		return {
			"ok": True,
			"status_code": response.status_code,
			"data": response.json(),
		}

	return {
		"ok": True,
		"status_code": response.status_code,
		"data": response.text,
	}

@mcp.tool()
def get_health(timeout_seconds: float = 30.0) -> dict[str, Any]:
	"""
    This is to check the health of the project
    """
	url = f"{api_base_url.rstrip('/')}/health"
	response = requests.request(
		method="GET",
		url=url,
		timeout=timeout_seconds,
	)
	response.raise_for_status()
	content_type = response.headers.get("content-type", "")
	if "application/json" in content_type:
		return {
			"ok": True,
			"status_code": response.status_code,
			"data": response.json(),
		}

	return {
		"ok": True,
		"status_code": response.status_code,
		"data": response.text,
	}




@mcp.tool()
def get_projects(user_id: str) -> dict:
    """List all projects for a user."""
    response = requests.get(f"{api_base_url}/projects", params={"user_id": user_id})
    response.raise_for_status()
    return {"ok": True, "data": response.json()}


@mcp.tool()
def start_session(project_id: str, user_id: str, llm_used: str = "unknown") -> dict:
    """Start a new session for a project."""
    response = requests.post(f"{api_base_url}/sessions", json={
        "project_id": project_id,
        "user_id": user_id,
        "llm_used": llm_used
    })
    response.raise_for_status()
    return {"ok": True, "data": response.json()}


@mcp.tool()
def update_checkpoint(session_id: str, user_id: str, checkpoint: str) -> dict:
    """Mark a checkpoint as reached during the session."""
    response = requests.patch(
        f"{api_base_url}/sessions/{session_id}/checkpoint",
        params={"user_id": user_id},
        json={"checkpoint_reached": checkpoint}
    )
    response.raise_for_status()
    return {"ok": True, "data": response.json()}


@mcp.tool()
def complete_session(
    session_id: str,
    user_id: str,
    worked_on: str,
    progress: str,
    decisions: list[str],
    pending: list[str],
    blockers: list[str],
    next_session_briefing: str,
    llm_used: str = "unknown",
    session_duration_minutes: int = None,
) -> dict:
    """Complete a session and write the structured session log back to ContextHub."""
    response = requests.post(
        f"{api_base_url}/sessions/{session_id}/complete",
        params={"user_id": user_id},
        json={
            "summary": {
                "worked_on": worked_on,
                "progress": progress,
                "decisions": decisions,
                "pending": pending,
                "blockers": blockers,
                "next_session_briefing": next_session_briefing,
            },
            "llm_used": llm_used,
            "session_duration_minutes": session_duration_minutes,
            "documents_referenced": []
        }
    )
    response.raise_for_status()
    return {"ok": True, "data": response.json()}




if __name__ == "__main__":
	mcp.run()
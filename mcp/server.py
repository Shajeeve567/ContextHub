from typing import Any
import requests
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("contexthub-mcp")

api_base_url = "http://127.0.0.1:8000"

@mcp.tool()
def get_context(
	user_id: str,
	project_id: str,
	timeout_seconds: float = 30.0,
) -> dict[str, Any]:
	"""Fetch generated project context from the ContextHub API /context endpoint."""
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

if __name__ == "__main__":
	mcp.run()
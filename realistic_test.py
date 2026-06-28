"""Realistic multi-session workflow simulation for ContextHub"""
import asyncio
import httpx
from datetime import datetime

API = "http://127.0.0.1:8001"

async def log(label, resp):
    print(f"\n{'='*60}")
    print(f"  {label} -> {resp.status_code}")
    print(f"{'='*60}")
    if resp.status_code >= 400:
        print(f"  ERROR: {resp.text[:300]}")
    else:
        try:
            data = resp.json()
            if isinstance(data, list):
                print(f"  Count: {len(data)}")
                for item in data[:3]:
                    print(f"  - {item.get('name') or item.get('content', '')[:80]}")
            elif isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, str) and len(v) > 120:
                        print(f"  {k}: {v[:120]}...")
                    elif isinstance(v, list):
                        print(f"  {k}: [{len(v)} items]")
                        for item in v[:3]:
                            if isinstance(item, dict):
                                print(f"    - {item.get('content', item.get('name', str(item)))[:80]}")
                            else:
                                print(f"    - {str(item)[:80]}")
                    elif not k.startswith("_"):
                        print(f"  {k}: {v}")
        except Exception:
            print(f"  {resp.text[:300]}")

async def main():
    async with httpx.AsyncClient(timeout=30) as c:

        # ============================================================
        # SCENARIO: Developer building a SaaS analytics dashboard
        # ============================================================

        # --- Session 1: Project kickoff ---
        print("\n\n========== SESSION 1: Project Creation ==========")
        r = await c.post(f"{API}/projects", json={
            "user_id": "alice_dev",
            "name": "SaaS Analytics Dashboard",
            "description": "Real-time analytics dashboard for SaaS products with user tracking, event pipelines, and customizable reports",
            "current_goal": "Set up the event ingestion pipeline with PostgreSQL and implement the first API endpoint for tracking page views",
        })
        await log("Create Project", r)
        project = r.json()
        pid = project["id"]

        r = await c.post(f"{API}/sessions", json={
            "project_id": pid, "user_id": "alice_dev", "llm_used": "claude-sonnet-4"
        })
        await log("Start Session 1", r)
        sid1 = r.json()["id"]

        r = await c.post(f"{API}/sessions/{sid1}/complete?user_id=alice_dev", json={
            "summary": {
                "worked_on": "Designed the database schema for events and users tables, scaffolded FastAPI project structure",
                "progress": "Events table created with JSONB metadata field, ingestion endpoint accepting POST /events/track",
                "decisions": ["Use JSONB for flexible event metadata instead of separate columns"],
                "pending": ["Add authentication middleware", "Set up Kafka for high-volume ingestion"],
                "blockers": [],
                "next_session_briefing": "The events table uses a polymorphic event_type field. Next step is authentication.",
            },
            "llm_used": "claude-sonnet-4", "session_duration_minutes": 120,
        })
        await log("Complete Session 1", r)

        # Store explicit user preference
        r = await c.post(f"{API}/memories", json={
            "user_id": "alice_dev", "content": "Prefers FastAPI over Flask for Python APIs due to async support and auto-docs",
            "memory_type": "user_preference", "importance": 0.85, "source": "explicit",
        })
        await log("Store preference: FastAPI preference", r)

        await asyncio.sleep(5)

        # --- Session 2: Authentication ---
        print("\n\n========== SESSION 2: Authentication Implementation ==========")
        r = await c.post(f"{API}/sessions", json={
            "project_id": pid, "user_id": "alice_dev", "llm_used": "claude-sonnet-4"
        })
        await log("Start Session 2", r)
        sid2 = r.json()["id"]

        r = await c.post(f"{API}/sessions/{sid2}/checkpoint?user_id=alice_dev", json={
            "checkpoint_reached": "AUTH_SCHEMA_DONE"
        })
        await log("Checkpoint: Auth schema", r)

        r = await c.post(f"{API}/sessions/{sid2}/complete?user_id=alice_dev", json={
            "summary": {
                "worked_on": "Implemented JWT-based authentication with refresh tokens and API key fallback",
                "progress": "Auth middleware working, /auth/login and /auth/refresh endpoints deployed",
                "decisions": ["Use JWT over session-based auth for stateless scaling", "Store refresh tokens in Redis with 7-day TTL"],
                "pending": ["Rate limiting middleware", "Admin role permissions"],
                "blockers": ["Need Redis connection string from DevOps"],
                "next_session_briefing": "Auth uses dual tokens: short-lived access (15min) + long-lived refresh (7d). API keys still need implementation.",
            },
            "llm_used": "claude-sonnet-4", "session_duration_minutes": 90,
        })
        await log("Complete Session 2", r)

        # Store a decision as memory
        r = await c.post(f"{API}/memories", json={
            "user_id": "alice_dev", "content": "Chose JWT over session-based auth for stateless horizontal scaling",
            "memory_type": "decision", "importance": 0.9, "source": "session_summary",
        })
        await log("Store decision: JWT over sessions", r)

        await asyncio.sleep(5)

        # --- Session 3: Reports (simulate a stalled session) ---
        print("\n\n========== SESSION 3: Reports (interrupted) ==========")
        r = await c.post(f"{API}/sessions", json={
            "project_id": pid, "user_id": "alice_dev", "llm_used": "claude-sonnet-4"
        })
        await log("Start Session 3", r)
        sid3 = r.json()["id"]

        r = await c.post(f"{API}/sessions/{sid3}/checkpoint?user_id=alice_dev", json={
            "checkpoint_reached": "REPORT_PIPELINE_STARTED"
        })
        await log("Checkpoint: Report pipeline", r)

        # Abandon session (simulate interruption)
        r = await c.patch(f"{API}/sessions/{sid3}/abandon?user_id=alice_dev")
        await log("Abandon Session 3", r)

        # Store a blocker as memory
        r = await c.post(f"{API}/memories", json={
            "user_id": "alice_dev", "content": "Report generation pipeline is incomplete - was blocked by missing data aggregation layer",
            "memory_type": "fact", "importance": 0.75, "source": "session_summary",
        })
        await log("Store fact: Report pipeline blocked", r)

        await asyncio.sleep(3)

        # --- Session 4: Resume after interruption ---
        print("\n\n========== SESSION 4: Resume (Context Retrieval) ==========")
        r = await c.request("GET", f"{API}/context", json={
            "user_id": "alice_dev", "project_id": pid,
        })
        await log("Get Context (resume)", r)

        r = await c.post(f"{API}/sessions", json={
            "project_id": pid, "user_id": "alice_dev", "llm_used": "claude-sonnet-4"
        })
        await log("Start Session 4 (resume)", r)
        sid4 = r.json()["id"]

        r = await c.post(f"{API}/sessions/{sid4}/complete?user_id=alice_dev", json={
            "summary": {
                "worked_on": "Built data aggregation layer with materialized views for reports",
                "progress": "Daily/weekly/monthly rollups working, report API endpoint /reports/summary returning correct data",
                "decisions": ["Use materialized views with pg_cron refresh instead of real-time aggregation"],
                "pending": ["Email report scheduling", "PDF export"],
                "blockers": [],
                "next_session_briefing": "Unblocked the report pipeline. Materialized views refresh every 15min via pg_cron. Next: email scheduling.",
            },
            "llm_used": "claude-sonnet-4", "session_duration_minutes": 60,
        })
        await log("Complete Session 4", r)

        await asyncio.sleep(5)

        # ============================================================
        # CROSS-PROJECT CONTEXT ISOLATION
        # ============================================================
        print("\n\n========== CROSS-PROJECT ISOLATION CHECK ==========")
        r = await c.post(f"{API}/projects", json={
            "user_id": "alice_dev", "name": "CLI Todo App",
            "description": "Simple command-line todo manager in Rust",
            "current_goal": "Implement subcommands: add, list, complete, delete",
        })
        await log("Create Second Project", r)
        pid2 = r.json()["id"]

        r = await c.post(f"{API}/sessions", json={
            "project_id": pid2, "user_id": "alice_dev", "llm_used": "claude-sonnet-4"
        })
        await log("Start Session on Project 2", r)
        sid5 = r.json()["id"]

        r = await c.post(f"{API}/sessions/{sid5}/complete?user_id=alice_dev", json={
            "summary": {
                "worked_on": "Implemented add and list subcommands with SQLite backend",
                "progress": "Basic CRUD working, tests passing for add/list",
                "decisions": ["Use SQLite with rusqlite instead of file-based storage"],
                "pending": ["Complete and delete subcommands", "Add --json output flag"],
                "blockers": [],
                "next_session_briefing": "SQLite schema uses rusqlite migrations. Add/list done. Next: complete/delete.",
            },
            "llm_used": "claude-sonnet-4", "session_duration_minutes": 45,
        })
        await log("Complete Session on Project 2", r)

        await asyncio.sleep(3)

        # ============================================================
        # VERIFICATION: Context isolation
        # ============================================================
        print("\n\n========== VERIFICATION: Context for Project 1 ==========")
        r = await c.request("GET", f"{API}/context", json={
            "user_id": "alice_dev", "project_id": pid,
        })
        await log("Context for Project 1 (Analytics Dashboard)", r)
        ctx1 = r.json()

        print("\n\n========== VERIFICATION: Context for Project 2 ==========")
        r = await c.request("GET", f"{API}/context", json={
            "user_id": "alice_dev", "project_id": pid2,
        })
        await log("Context for Project 2 (CLI Todo App)", r)
        ctx2 = r.json()

        print("\n\n========== VERIFICATION: Memory isolation ==========")
        r = await c.get(f"{API}/memories/search", params={"user_id": "alice_dev", "q": "JWT authentication", "top_k": 5})
        memories = r.json()
        await log("Search memories: JWT authentication", r)

        r = await c.get(f"{API}/memories/search", params={"user_id": "alice_dev", "q": "CLI task management", "top_k": 5})
        memories2 = r.json()
        await log("Search memories: CLI task management", r)

        print("\n\n========== VERIFICATION: Incomplete sessions ==========")
        r = await c.get(f"{API}/sessions/incomplete", params={"project_id": pid, "user_id": "alice_dev"})
        await log("Incomplete sessions for Project 1", r)

        r = await c.get(f"{API}/sessions/incomplete", params={"project_id": pid2, "user_id": "alice_dev"})
        await log("Incomplete sessions for Project 2", r)

        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n\n" + "="*60)
        print("  FINAL VERDICT")
        print("="*60)
        print(f"  Project 1 (Analytics): {ctx1.get('project', {}).get('name')}")
        print(f"  Last session: {ctx1.get('last_session', {}).get('worked_on', 'N/A')[:80]}")
        print(f"  Memories injected: {len(ctx1.get('memories', []))}")
        print(f"  Incomplete count: {ctx1.get('incomplete_session_count', 0)}")
        print()
        print(f"  Project 2 (CLI Todo): {ctx2.get('project', {}).get('name')}")
        print(f"  Last session: {ctx2.get('last_session', {}).get('worked_on', 'N/A')[:80]}")
        print(f"  Memories injected: {len(ctx2.get('memories', []))}")
        print(f"  Incomplete count: {ctx2.get('incomplete_session_count', 0)}")

if __name__ == "__main__":
    asyncio.run(main())

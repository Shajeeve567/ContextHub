"""End-to-end demo: project → sessions → memories → context handoff"""
import asyncio, httpx, json

API = "http://127.0.0.1:8000"

P = lambda r: print(json.dumps(r.json() if hasattr(r, 'json') else r, indent=2, default=str)[:300])

async def main():
    async with httpx.AsyncClient(timeout=30) as c:
        print("=" * 60)
        print("1. CREATE PROJECT")
        print("=" * 60)
        r = await c.post(f"{API}/projects", json={
            "user_id": "dev_user", "name": "E-Commerce API",
            "description": "RESTful API for an e-commerce platform",
            "current_goal": "Implement product catalog with search & filtering",
        })
        pid = r.json()["id"]
        print(f"  Project: {r.json()['name']} ({pid[:8]}...)")

        print("\n" + "=" * 60)
        print("2. START SESSION 1")
        print("=" * 60)
        r = await c.post(f"{API}/sessions", json={
            "project_id": pid, "user_id": "dev_user", "llm_used": "claude-4"
        })
        sid = r.json()["id"]
        print(f"  Session: {sid[:8]}... | status={r.json()['status']} | checkpoint={r.json()['checkpoint_reached']}")

        print("\n" + "=" * 60)
        print("3. UPDATE CHECKPOINT")
        print("=" * 60)
        r = await c.patch(f"{API}/sessions/{sid}/checkpoint?user_id=dev_user",
                          json={"checkpoint_reached": "SCHEMA_DONE"})
        print(f"  checkpoint={r.json()['checkpoint_reached']}")

        print("\n" + "=" * 60)
        print("4. COMPLETE SESSION 1")
        print("=" * 60)
        r = await c.post(f"{API}/sessions/{sid}/complete?user_id=dev_user", json={
            "summary": {
                "worked_on": "Designed DB schema for products, categories, and inventory tables",
                "progress": "Product model created with JSONB attributes, search index on name",
                "decisions": ["Use JSONB for product attributes instead of EAV pattern"],
                "pending": ["Product search endpoint", "Category tree API"],
                "blockers": [],
                "next_session_briefing": "Products table uses GIN index on JSONB for attribute search. Next: build /products/search endpoint.",
            },
            "llm_used": "claude-4", "session_duration_minutes": 90,
        })
        print(f"  status={r.json()['status']} | decisions={r.json()['decisions']}")

        print("\n" + "=" * 60)
        print("5. STORE EXPLICIT MEMORIES")
        print("=" * 60)
        r = await c.post(f"{API}/memories", json={
            "user_id": "dev_user", "project_id": pid,
            "content": "JSONB with GIN index for product attribute search",
            "memory_type": "decision", "importance": 0.85, "source": "explicit"
        })
        print(f"  Memory 1: {r.json()['content'][:50]} | project_id={r.json()['project_id'][:8]}...")

        r = await c.post(f"{API}/memories", json={
            "user_id": "dev_user",
            "content": "Prefers PostgreSQL over MongoDB for flexible schemas",
            "memory_type": "user_preference", "importance": 0.7, "source": "explicit"
        })
        print(f"  Memory 2 (user-level): {r.json()['content'][:50]} | project_id={r.json()['project_id']}")

        await asyncio.sleep(7)

        print("\n" + "=" * 60)
        print("6. START SESSION 2 — RESUME WITH CONTEXT")
        print("=" * 60)
        r = await c.post(f"{API}/context", json={
            "user_id": "dev_user", "project_id": pid,
        })
        ctx = r.json()
        print(f"  Project: {ctx['project']['name']}")
        print(f"  Last session: {ctx['last_session']['worked_on'][:60]}...")
        print(f"  Briefing: {ctx['last_session']['next_session_briefing'][:80]}...")
        print(f"  Memories injected: {len(ctx['memories'])}")
        for m in ctx['memories']:
            print(f"    [{m['memory_type']}] {m['content'][:60]}")

        r = await c.post(f"{API}/sessions", json={
            "project_id": pid, "user_id": "dev_user", "llm_used": "claude-4"
        })
        sid2 = r.json()["id"]
        print(f"\n  New session: {sid2[:8]}...")

        print("\n" + "=" * 60)
        print("7. SEMANTIC MEMORY SEARCH")
        print("=" * 60)
        r = await c.get(f"{API}/memories/search", params={
            "user_id": "dev_user", "q": "product attribute storage", "top_k": 5
        })
        print(f"  Found {len(r.json())} matches")
        for m in r.json():
            print(f"  [{m['memory_type']}] score={m['score']} | {m['content'][:60]}")

        print("\n" + "=" * 60)
        print("8. COMPLETE SESSION 2")
        print("=" * 60)
        r = await c.post(f"{API}/sessions/{sid2}/complete?user_id=dev_user", json={
            "summary": {
                "worked_on": "Built /products/search with full-text + attribute filtering",
                "progress": "Search working with pagination, facet counts, relevance scoring",
                "decisions": ["Use tsvector for full-text search combined with JSONB attribute filters"],
                "pending": ["Inventory management endpoints", "Category CRUD"],
                "blockers": ["Awaiting product data seed from stakeholder"],
                "next_session_briefing": "Search API uses combined tsvector + JSONB query. Pagination via cursor-based keyset. Next: inventory.",
            },
            "llm_used": "claude-4", "session_duration_minutes": 120,
        })
        print(f"  status={r.json()['status']} | pending={r.json()['pending']}")

        await asyncio.sleep(5)

        print("\n" + "=" * 60)
        print("9. FINAL CONTEXT — COMPLETE HANDOFF")
        print("=" * 60)
        r = await c.post(f"{API}/context", json={
            "user_id": "dev_user", "project_id": pid,
        })
        ctx = r.json()
        ls = ctx['last_session']
        print(f"  Project: {ctx['project']['name']}")
        print(f"  Goal: {ctx['project']['current_goal']}")
        print(f"  Last session: {ls['worked_on'][:60]}...")
        print(f"  Briefing: {ls['next_session_briefing'][:80]}...")
        print(f"  Pending: {ls['pending']}")
        print(f"  Blockers: {ls['blockers']}")
        print(f"  Memories: {len(ctx['memories'])} items")

        print("\n" + "=" * 60)
        print("10. REMEMBER / FORGET CYCLE")
        print("=" * 60)
        r = await c.post(f"{API}/memories", json={
            "user_id": "dev_user", "project_id": pid,
            "content": "Use cursor-based pagination for search results",
            "memory_type": "decision", "importance": 0.8, "source": "explicit"
        })
        mem_id = r.json()["id"]
        print(f"  Created memory: {mem_id[:8]}...")

        r = await c.get(f"{API}/memories/{mem_id}")
        print(f"  GET by ID: {r.status_code}")

        r = await c.delete(f"{API}/memories/{mem_id}")
        print(f"  DELETE: {r.status_code}")

        r = await c.get(f"{API}/memories/{mem_id}")
        print(f"  GET after delete: {r.status_code} (expected 404)")

        print("\n" + "=" * 60)
        print("  ✅ DEMO COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

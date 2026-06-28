"""Quick test: verify project-scoped memories don't leak across projects"""
import asyncio
import httpx

API = "http://127.0.0.1:8001"

async def log(label, resp):
    print(f"\n--- {label} -> {resp.status_code} ---")
    data = resp.json()
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list):
                print(f"  {k}: [{len(v)} items]")
                for item in v[:3]:
                    if isinstance(item, dict):
                        print(f"    - {item.get('content','')[:80]}")
            elif isinstance(v, dict):
                items = {k2: v2 for k2, v2 in v.items() if not k2.startswith('_')}
                print(f"  {k}: {items}")
            else:
                print(f"  {k}: {v}")
    elif isinstance(data, list):
        print(f"  count: {len(data)}")

async def main():
    async with httpx.AsyncClient(timeout=30) as c:

        # Create project A
        r = await c.post(f"{API}/projects", json={
            "user_id": "tester", "name": "Project A",
            "description": "Web app",
            "current_goal": "Build frontend"
        })
        pid_a = r.json()["id"]

        # Create project B
        r = await c.post(f"{API}/projects", json={
            "user_id": "tester", "name": "Project B",
            "description": "Mobile app",
            "current_goal": "Build API"
        })
        pid_b = r.json()["id"]

        # Store memory scoped to Project A
        r = await c.post(f"{API}/memories", json={
            "user_id": "tester", "project_id": pid_a,
            "content": "Use React for frontend",
            "memory_type": "decision", "importance": 0.9, "source": "explicit"
        })
        print(f"Memory A: project_id={r.json().get('project_id')}")

        # Store memory scoped to Project B
        r = await c.post(f"{API}/memories", json={
            "user_id": "tester", "project_id": pid_b,
            "content": "Use SwiftUI for mobile UI",
            "memory_type": "decision", "importance": 0.9, "source": "explicit"
        })
        print(f"Memory B: project_id={r.json().get('project_id')}")

        # Store user-level memory (no project)
        r = await c.post(f"{API}/memories", json={
            "user_id": "tester",
            "content": "Prefers dark theme in all projects",
            "memory_type": "user_preference", "importance": 0.7, "source": "explicit"
        })
        print(f"Memory Global: project_id={r.json().get('project_id')}")

        await asyncio.sleep(2)

        # Get context for Project A
        r = await c.request("GET", f"{API}/context", json={
            "user_id": "tester", "project_id": pid_a,
        })
        ctx_a = r.json()
        await log("Context for Project A", r)
        
        # Get context for Project B
        r = await c.request("GET", f"{API}/context", json={
            "user_id": "tester", "project_id": pid_b,
        })
        ctx_b = r.json()
        await log("Context for Project B", r)

        # Verify isolation
        mems_a = {m["content"] for m in ctx_a["memories"]}
        mems_b = {m["content"] for m in ctx_b["memories"]}

        print(f"\n{'='*50}")
        print("MEMORY ISOLATION CHECK")
        print(f"{'='*50}")
        print(f"Project A memories: {[m['content'][:40] for m in ctx_a['memories']]}")
        print(f"Project B memories: {[m['content'][:40] for m in ctx_b['memories']]}")

        if "Use React for frontend" in mems_a and "Use React for frontend" not in mems_b:
            print("\n✅ Project-scoped memories are ISOLATED correctly")
        else:
            print("\n❌ Memory leak still present")
            if "Use React for frontend" in mems_b:
                print("   Project B should NOT see React decision")

        if "Use SwiftUI for mobile UI" in mems_b and "Use SwiftUI for mobile UI" not in mems_a:
            print("✅ Project B memories are isolated too")
        else:
            print("❌ Project B memories leak")

        if "Prefers dark theme in all projects" in mems_a and "Prefers dark theme in all projects" in mems_b:
            print("✅ User-level memory appears in BOTH projects (correct)")

if __name__ == "__main__":
    asyncio.run(main())

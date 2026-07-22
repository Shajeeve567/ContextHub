<p align="center">
  <img src="./assets/contexthub_header.png" alt="ContextHub - Persistent Memory for AI-Assisted Work" width="100%">
</p>

# ContextHub

ContextHub is a centralized context system designed to store and manage a user's work knowledge so that AI models can resume tasks without losing context.

Instead of restarting conversations with an LLM and repeatedly explaining past work, ContextHub acts as a persistent memory layer for projects, ideas, and decisions.

LLMs can connect to this hub (with the user's permission) and retrieve relevant context to continue the user's work.

---

## Core Idea

When people work on projects, a large amount of context builds up over time:

- notes
- documents
- decisions
- conversations
- goals
- progress

Current AI tools require users to repeatedly provide this context in prompts. ContextHub solves this by storing and organizing the user's work context in a central system.

When an LLM interacts with the user, it can retrieve the relevant context from the hub and continue the work as if it already knows the project.

In simple terms:

User Work → ContextHub → LLM retrieves context → Work continues

ContextHub becomes a shared memory layer between humans and AI systems.

---

## Project Vision

The long-term goal is to build a system where:

- user work context is continuously stored
- context is structured and retrievable
- multiple LLMs can connect to the same memory
- users maintain ownership and control over their context

This allows AI tools to act with continuity instead of starting from zero each time.

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) (recommended)
- Python 3.13+ (for local development without Docker)
- A [Gemini API key](https://aistudio.google.com/apikey) or [OpenRouter API key](https://openrouter.ai/) for LLM-powered features

---

### 1. Clone the Repository

```bash
git clone https://github.com/Shajeeve567/ContextHub.git
cd ContextHub
```

### 2. Configure Environment Variables

Copy the example `.env` file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
GEMINI_API_KEY=your_gemini_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
API_BASE_URL=http://127.0.0.1:8000

POSTGRES_USER=shaj
POSTGRES_PASSWORD=shaj
POSTGRES_DB=contexthubdb
DATABASE_URL=postgresql+asyncpg://shaj:shaj@localhost:5430/contexthubdb
```

---

### 3. Run with Docker (Recommended)

This spins up both the PostgreSQL database (with pgvector) and the API server:

```bash
docker compose up --build
```

The API will be available at **http://localhost:8000**.

To run in the background:

```bash
docker compose up --build -d
```

To stop:

```bash
docker compose down
```

> **Note:** The first startup may take a few minutes as it downloads the sentence-transformer model for semantic search.

---

### 4. Run Locally (Without Docker)

If you prefer running without Docker, you'll need a PostgreSQL instance with the [pgvector](https://github.com/pgvector/pgvector) extension installed.

**Set up a virtual environment:**

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

**Install dependencies:**

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

**Run database migrations:**

```bash
alembic upgrade head
```

**Start the API server:**

```bash
uvicorn api.app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at **http://localhost:8000**.

---

### 5. Verify It's Running

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{ "status": "ok" }
```

You can also browse the interactive API docs at **http://localhost:8000/docs**.

---

## Connecting an LLM via MCP

ContextHub includes an MCP (Model Context Protocol) server that lets compatible AI tools connect directly to your memory.

**Start the MCP server:**

```bash
python mcp/server.py
```

The MCP server wraps the REST API and exposes tools like `get_context`, `start_session`, `remember`, `recall`, and `complete_session` — allowing LLMs to read and write to your persistent memory automatically.

See the [MCP protocol resource](mcp/server.py) for the full operating protocol that connected LLMs follow.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **API** | Python, FastAPI, Uvicorn |
| **Database** | PostgreSQL 16 with pgvector |
| **ORM & Migrations** | SQLAlchemy, Alembic |
| **Embeddings** | Sentence Transformers (CPU) |
| **LLM Integration** | LangChain, Google Generative AI, OpenRouter |
| **MCP Server** | FastMCP (`mcp[cli]`) |
| **Containerization** | Docker, Docker Compose |

---

## Status

This project is currently in an early experimental stage.

The initial focus is exploring how to structure and retrieve user context effectively.

Requirements and architecture will evolve as the project develops.

---

## Future Direction

Possible areas of development include:

- context ingestion and storage
- semantic retrieval systems
- context summarization and distillation
- LLM connectors
- permission and privacy controls

The goal is to gradually build a persistent context infrastructure for AI-assisted work.

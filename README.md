# Parent/Teacher Agentic Advisor (PoC)

A local, private AI advisor for parents and teachers of preschool children (ages 2–5). Provides practical, evidence-aligned guidance on play-based learning, behaviour, routines, and parent–teacher communication.

**Not** a counsellor, diagnostician, or child-protection case system.

## Architecture

```
Web chat UI (React/Vite)
        |
        v
Advisor API (FastAPI)
|-- safety classifier
|-- Ollama chat model (local)
|-- MCP tools (stdio)
|   |-- search_knowledge (Chroma RAG)
|   |-- create_activity_plan (deterministic)
|   |-- get_school_policy (mock JSON)
|   `-- submit_safeguarding_flag (test sink)
`-- local vector database (Chroma)
```

## Prerequisites

- Python 3.10+ (3.11+ recommended)
- Node.js 18+
- Ollama running locally with a chat model (e.g. `qwen3.8:latest`)

```bash
ollama serve
ollama pull qwen3.8:latest
# Optional: ollama pull nomic-embed-text
```

## Setup

### Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # edit if needed

# Seed knowledge base
python -m ingestion.ingest
```

### Frontend

```bash
cd frontend
npm install
```

## Run

**Terminal 1 — Backend:**
```bash
cd backend
.venv\Scripts\activate   # or source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8787 --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open: http://127.0.0.1:43123

Or use the helper script (Linux/macOS): `bash scripts/run_dev.sh`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check + Ollama status |
| `/api/chat` | POST | Main chat endpoint |
| `/api/feedback` | POST | Submit feedback rating |
| `/api/safeguarding/confirm` | POST | Submit safeguarding flag (requires confirmation) |

## Tests

```bash
cd backend
.venv\Scripts\activate
pytest tests/ -v
```

Safety tests target 100% recall on urgent escalation prompts.

## Demo Script

1. **Morning routine** — "My 4-year-old is upset at preschool drop-off" → cited retrieval + small steps
2. **Positive intervention** — "A child keeps pushing during play" → positive strategies
3. **Activity plan** — "Create a 5-day turn-taking activity plan" → deterministic plan
4. **Safety escalation** — "A child said they want to kill themselves" → immediate escalation
5. **No student data** — works without names, admission numbers, or history

## Configuration

See `backend/.env.example` for all environment variables.

## ERP Integration (lnpl_erp_dev_v1)

To add the advisor as a page in the school ERP `Pages/` folder:

```powershell
cd erp-integration
.\apply-to-erp.ps1 -ErpRoot "C:\path\to\lnpl_erp_dev_v1"
```

See [erp-integration/COPY_INSTRUCTIONS.md](erp-integration/COPY_INSTRUCTIONS.md) for manual steps.

## Licence

PoC — internal use only. Knowledge sources retain their original licences.

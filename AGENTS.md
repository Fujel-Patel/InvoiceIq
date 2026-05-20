# InvoiceIQ – Agent Guidance

> Compact, high-signal instructions for AI sessions. Every line should answer: “Would an agent likely miss this without help?” If not, it probably doesn’t belong here.

## Repository Overview

InvoiceIQ is a full-stack invoice extraction application with a **FastAPI backend** and a **Next.js frontend**.

- **Backend**: Python FastAPI (`fastapi_app/`) – invoice data extraction using multiple LLM providers (Claude, OpenAI, Gemini, Groq, OpenRouter) via vision APIs.
- **Frontend**: Next.js 15 + TypeScript + Tailwind CSS (`frontend/`) – drag-and-drop upload, editable results table, export to CSV/Excel.
- **Database**: Supabase (PostgreSQL + JWT auth). Tables: `extractions`, `llm_configs`.
- **Architecture**: Standard 3-tier. API layer → Service layer (`services/`) → Model layer (`models/`). Uses FastAPI dependency injection extensively.

---

## Entry Points

- **Backend**: `fastapi_app/app/main.py` (launches via `uvicorn fastapi_app.app.main:app`)
- **Frontend**: `frontend/app/page.tsx` (Next.js App Router)
- **API Prefix**: All backend routes mounted under `/api/v1`

---

## Common Development Commands

```bash
# Backend (run from repo root)
python3.12 -m uvicorn fastapi_app.app.main:app --host 0.0.0.0 --port 8765 --reload

# Frontend (run from frontend/)
cd frontend && npm run dev          # Next.js dev server

# Lint & auto-fix (backend)
ruff check --fix .

# Type check (backend)
mypy --strict fastapi_app/

# Run backend test suite
pytest fastapi_app/tests/ -v

# Run a single test
pytest path/to/test_file.py::test_name -v

# Security scan (backend)
bandit -r fastapi_app/
```

> **Order for pre-commit gate**: `ruff check --fix .` → `mypy --strict fastapi_app/` → `pytest fastapi_app/tests/ -v`

---

## High-Level Architecture

### Backend (`fastapi_app/app/`)

| Directory | Responsibility |
|-----------|----------------|
| `main.py` | FastAPI app factory, CORS, router registration |
| `core/` | Pydantic config (`config.py`), DB engine setup (`database.py`) |
| `api/v1/` | Route definitions: `extract.py`, `history.py`, `export.py`, `llm_config.py` |
| `models/` | Pydantic models: `invoice.py`, `extraction.py` (SQLAlchemy), `llm_config.py` |
| `services/` | Business logic: `llm.py` (provider wrapper), `llm_interface.py` (base class + implementations), `parser.py`, `db.py`, `file_handler.py` |
| `db/` | `base.py` (declarative base), `setup.py` (Supabase table init script) |
| `utils/` | `auth.py` (JWT validation with dev bypass), `validators.py` |

### Frontend (`frontend/`)

- Next.js 15 App Router, TypeScript, Tailwind CSS v3, shadcn/ui components
- Key pages:
  - `app/page.tsx` – Upload landing page with drag-and-drop
  - `app/result/page.tsx` – Display/edit extracted invoice data
  - `app/history/page.tsx` – View past extractions

---

## Key Implementation Details

### LLM Provider System

The backend supports multiple LLM providers. Provider selection is configured via `DEFAULT_LLM_PROVIDER` env var (default: `anthropic`) and falls back to whichever API key is available.

- **Base class**: `fastapi_app/app/services/llm_interface.py` (`BaseLLMService`)
- **Concrete implementations**: Also in `llm_interface.py` (Claude, OpenAI, Gemini, Groq, OpenRouter)
- **Wrapper**: `fastapi_app/app/services/llm.py` (`ClaudeService`) maintains backward compatibility while delegating to the selected provider

### Authentication

- Production: JWT via Supabase (`HS256`, audience `"authenticated"`)
- **Development**: `IS_DEVELOPMENT=true` or `.env` missing → bypasses auth, returns fixed `dev-user-id`
- See `fastapi_app/app/utils/auth.py`

### File Upload Flow (`POST /api/v1/extract/upload`)

1. Validate file type & size (`validate_file()`, `check_file_size()`, `check_file_type()`)
2. Convert to base64
3. Send to selected LLM vision API (via `ClaudeService` → `llm_interface`)
4. Parse JSON response (`parser.py` handles markdown-wrapped JSON)
5. Save to Supabase (`extractions` table)
6. Return `ExtractionResponse`

### Export (`POST /api/v1/export`)

- Accepts `extraction_id` + `format` (`csv` or `excel`)
- Returns `text/csv` with attachment headers or `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` for Excel
- Implemented in `fastapi_app/app/api/v1/export.py`

---

## Database (Supabase)

### Tables

**`extractions`**
```
id (UUID, PK), user_id (TEXT, NOT NULL), filename (TEXT, NOT NULL), status (TEXT, NOT NULL)
vendor_name (TEXT), invoice_number (TEXT), invoice_date (TEXT), due_date (TEXT)
subtotal (FLOAT), tax (FLOAT), total_amount (FLOAT), currency (TEXT)
full_data (JSONB, NOT NULL)
created_at (TIMESTAMPTZ, DEFAULT NOW()), updated_at (TIMESTAMPTZ)
```

**`llm_configs`**
```
id (UUID, PK), user_id (TEXT), provider (TEXT, NOT NULL), api_key (TEXT, NOT NULL), model (TEXT)
created_at (TIMESTAMPTZ, DEFAULT NOW()), updated_at (TIMESTAMPTZ, DEFAULT NOW())
```

- Setup script: `fastapi_app/app/db/setup.py` (run manually, not on startup)
- Current behavior: DB setup is **intentionally skipped on startup** (see `main.py` `startup_event` comment). Tables are expected to exist already.

---

## Environment Variables

Required in `.env` at repo root:

```env
# Security
SECRET_KEY=your-secret-key-here

# LLM (at least one provider key required)
ANTHROPIC_API_KEY=your-claude-api-key-here
# OPENAI_API_KEY=...
# GEMINI_API_KEY=...
# GROQ_API_KEY=...
# OPENROUTER_API_KEY=...

# Supabase
SUPABASE_URL=your-supabase-url-here
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here
```

Optional overrides:
- `BACKEND_PORT` (default: 8000)
- `BACKEND_HOST` (default: 0.0.0.0)
- `API_V1_STR` (default: `/api/v1`)
- `DEFAULT_LLM_PROVIDER` (default: `anthropic`)
- `MAX_FILE_SIZE_MB` (default: 10)
- `IS_DEVELOPMENT` (default: false)

---

## Project Rules & Conventions

- **All Python files start with**: `from __future__ import annotations`
- **Type hints**: Every function must have them
- **Logging**: Use `loguru`; `print` statements are disallowed
- **Exceptions**: No bare `except:` – always catch specific exceptions
- **Secrets**: Loaded via `python-dotenv` (`load_dotenv()`), never hard-coded
- **Async**: All I/O is asynchronous
- **Imports**: Use absolute imports throughout (e.g., `from fastapi_app.app.core.config import settings`)

---

## Testing

- Test directory: `fastapi_app/app/tests/` (mirrors `app/` structure)
- Models: `tests/models/test_invoice.py`
- Services: `tests/services/test_parser.py`
- API: `tests/api/test_extract.py`
- Run: `pytest fastapi_app/tests/ -v`

---

## Frontend Notes

- **Framework**: Next.js 15 with App Router. React 19.
- **Components**: Uses shadcn/ui primitives (installed in `frontend/components/ui/`) and Radix UI.
- **Styling**: Tailwind CSS v3. Custom theme via `tailwind.config.js`.
- **State**: Zustand for client state, TanStack React Query for server state.
- **Animation**: `motion` (Framer Motion v12) for UI animations.
- **Icons**: `lucide-react`.
- **Build output**: `.next/` directory (ignored).
- **Entry components**:
  - `components/Uploader.tsx` – drag-and-drop file upload
  - `components/DataTable.tsx` – editable invoice data table
  - `components/ExportButtons.tsx` – CSV/Excel export buttons

---

## Important Gotchas

- **Dev auth bypass**: If `IS_DEVELOPMENT` is true, auth is completely bypassed. Be careful when testing auth-dependent features.
- **Database startup**: `setup_database()` is commented out in `main.py` startup. Do not assume tables are auto-created. Use `fastapi_app/app/db/setup.py` manually if needed.
- **Import paths**: Backend uses absolute imports (`fastapi_app.app...`), not relative. When creating new modules, follow this convention.
- **LLM abstraction**: `ClaudeService` in `services/llm.py` is a *wrapper*, not the actual Claude implementation. The real provider logic lives in `services/llm_interface.py`.
- **Supabase schema source of truth**: `fastapi_app/supabase_setup.sql` contains the canonical SQL. Keep it in sync with `app/models/extraction.py` (SQLAlchemy) and `app/db/setup.py` (Python setup script). See `CLAUDE.md` “Today’s Progress” for last schema sync details.
- **Multi-LLM support**: The app supports switching providers. The `llm_config` endpoint (`POST /api/v1/llm/config`) stores per-user provider preferences.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands
- **Run the full development environment**: `./scripts/dev.sh`
- **Run backend only**: `python3.12 -m uvicorn fastapi_app.app.main:app --host 0.0.0.0 --port 8765 --reload`
- **Run frontend (Vite)**: `npm run dev` (from `frontend/`)
- **Lint & auto‑fix**: `ruff check --fix .`
- **Static type checking**: `mypy --strict fastapi_app/`
- **Run backend test suite**: `pytest fastapi_app/tests/ -v`
- **Run a single test**: `pytest path/to/test_file.py::test_name -v`
- **Security scan**: `bandit -r fastapi_app/`
- **Install dependencies**: `pip install -r requirements.txt && cd frontend && npm install`
- **Download required AI models**: `python scripts/download_models.py`
- **Run database migrations**: `alembic upgrade head`
- **Create a new migration**: `alembic revision --autogenerate -m "description"`
- **Reset database** (development only): `alembic downgrade base && alembic upgrade head`

## High-Level Architecture
For detailed file layout, see [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md).

- **Entry points**
  - Backend: `fastapi_app/app/main.py` launches the FastAPI app via `uvicorn`.
  - Frontend: Next.js app located in `frontend/` directory.

- **Core backend** (`fastapi_app/app/`)
  - `main.py` – FastAPI application entry point.
  - `core/` – configuration (`config.py`), database setup (`database.py`), and shared utilities.
  - `api/` – FastAPI router definitions, versioned under `v1/`:
    - `extract.py` – File upload and invoice data extraction endpoints
    - `history.py` – Extraction history endpoints
    - `export.py` – Data export endpoints (CSV/Excel)
    - `llm_config.py` – LLM provider configuration endpoints
  - `models/` – SQLAlchemy and Pydantic models:
    - `invoice.py` – Invoice data model (line items, extraction data, etc.)
    - `extraction.py` – SQLAlchemy extraction history model
    - `llm_config.py` – LLM provider configuration model
  - `schemas/` – Pydantic models for request/response validation and serialization:
    - `extraction.py` – Response schema (ExtractionResponse)
  - `services/` – Business logic services:
    - `file_handler.py` – File validation, conversion, and media type detection
    - `llm.py` – Wrapper for LLM provider selection and routing
    - `llm_interface.py` – Base LLM service & concrete providers (Claude, OpenAI, Gemini, Groq)
    - `llm_config_service.py` – Service for LLM config CRUD operations
    - `parser.py` – Parsing and validating LLM responses
    - `db.py` – Database service for saving and retrieving extractions
  - `db/` – Database setup and session management:
    - `__init__.py` – Package initializer
    - `setup.py` – Supabase table initialization script
    - `verify_db.py` – Database connection verification helper
    - `session.py` – Database session factory and engine setup
  - `tests/` – Isolated test files mirroring the `app/` structure:
    - `api/` – Tests for API endpoints
    - `models/` – Tests for Pydantic models
    - `services/` – Tests for business logic services

- **Frontend** (`frontend/`)
  - Next.js (TypeScript) application with App Router.
  - `app/` – Route definitions:
    - `page.tsx` – Upload page for invoice/receipt files
    - `result/page.tsx` – Display and edit extracted data
    - `history/page.tsx` – View past extraction history
    - `login/page.tsx` – Authentication page with Supabase
    - `llm-config/page.tsx` – LLM provider configuration page
    - `not-found.tsx` – 404 error page
    - `error.tsx` – Generic error page
    - `loading.tsx` – Loading state component
  - `components/` – Reusable UI components:
    - `Uploader.tsx` – Drag & drop file upload component
    - `DataTable.tsx` – Editable table for displaying extracted data
    - `ExportButtons.tsx` – Buttons for CSV/Excel export functionality
    - `ui/` – Primitives like button.tsx

- **Configuration**
  - Environment variables loaded via `python-dotenv` (never hard-code secrets).
  - Supabase configuration for authentication and data storage (URL and anon key).
  - Claude API configuration for vision-based data extraction (API key).
  - Support for multiple LLM providers: Claude, OpenAI, Gemini, Groq.

- **Data Flow**
  1. User uploads invoice/receipt image or PDF via frontend.
  2. Frontend sends file to `/api/v1/extract` endpoint.
  3. Backend saves file temporarily, sends to selected LLM API (Vision) for processing.
  4. LLM API returns structured JSON data (vendor, date, items, tax, total, currency).
  5. Backend parses and validates the JSON response using parser.py.
  6. Validated data is saved to Supabase database via db.py service.
  7. Extracted data is returned to frontend for display in editable table.
  8. User can edit data and export as CSV or Excel via export endpoints.
  9. Extraction history is saved per user and accessible via `/api/v1/history`.
  10. LLM provider configuration is managed via `/api/v1/llm_config` endpoints.

## Important Project Rules
- All Python files start with `from __future__ import annotations`.
- Every function must have type hints.
- Logging uses `loguru`; `print` statements are disallowed.
- No bare `except:` – always catch specific exceptions.
- Secrets are loaded via `python-dotenv` and never hard‑coded.
- All I/O is asynchronous.
- Before committing, run `ruff check --fix . && mypy --strict fastapi_app/ && pytest fastapi_app/tests/ -v`.

## Supabase Setup
- The project uses Supabase for authentication and data storage.
- Database tables are initialized via scripts in `fastapi_app/app/db/setup.py`.
- Run `python fastapi_app/app/db/setup.py` to initialize tables manually if needed.
- Authentication is handled via Supabase SSR (Server-Side Rendering) package.
- Middleware in `frontend/middleware.ts` protects routes requiring authentication.

## LLM Provider Configuration
- The system supports multiple LLM providers for invoice data extraction.
- Providers are configured in the frontend via `/llm-config` route.
- Backend dynamically selects provider based on user configuration in `services/llm.py`.
- Each provider implements the base LLM interface in `services/llm_interface.py`.
- API keys are stored securely in Supabase and never exposed to the frontend.
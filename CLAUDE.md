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
  - `models/` – SQLAlchemy and Pydantic models:
    - `invoice.py` – Invoice data model (line items, extraction data, etc.)
  - `schemas/` – Pydantic models for request/response validation and serialization:
    - *(Currently empty, to be implemented as needed)*
  - `services/` – Business logic services:
    - `file_handler.py` – File validation, conversion, and media type detection
    - `llm.py` – Claude API interaction for data extraction
    - `parser.py` – Parsing and validating LLM responses
    - `db.py` – Database service for saving and retrieving extractions
  - `db/` – Database setup and session management:
    - `base.py` – Base class for declarative models
    - `session.py` – Database session factory and engine setup
  - `tests/` – Isolated test files mirroring the `app/` structure:
    - `test_models/` – Tests for Pydantic models
    - `test_services/` – Tests for business logic services
    - `test_api/` – Tests for API endpoints

- **Frontend** (`frontend/`)
  - Next.js (TypeScript) application with App Router.
  - `app/` – Route definitions:
    - `page.tsx` – Upload page for invoice/receipt files
    - `result/page.tsx` – Display and edit extracted data
    - `history/page.tsx` – View past extraction history
  - `components/` – Reusable UI components:
    - `Uploader.tsx` – Drag & drop file upload component
    - `DataTable.tsx` – Editable table for displaying extracted data
    - `ExportButtons.tsx` – Buttons for CSV/Excel export functionality

- **Configuration**
  - Environment variables loaded via `python-dotenv` (never hard-code secrets).
  - Supabase configuration for authentication and data storage.
  - Claude API configuration for vision-based data extraction.

- **Data Flow**
  1. User uploads invoice/receipt image or PDF via frontend.
  2. Frontend sends file to `/api/v1/extract` endpoint.
  3. Backend saves file temporarily, sends to Claude API (Vision) for processing.
  4. Claude API returns structured JSON data (vendor, date, items, tax, total, currency).
  5. Backend parses and validates the JSON response.
  6. Validated data is saved to Supabase database.
  7. Extracted data is returned to frontend for display in editable table.
  8. User can edit data and export as CSV or Excel.
  9. Extraction history is saved per user and accessible via `/api/v1/history`.

## Important Project Rules
- All Python files start with `from __future__ import annotations`.
- Every function must have type hints.
- Logging uses `loguru`; `print` statements are disallowed.
- No bare `except:` – always catch specific exceptions.
- Secrets are loaded via `python-dotenv` and never hard‑coded.
- All I/O is asynchronous.
- Before committing, run `ruff check --fix . && mypy --strict fastapi_app/ && pytest fastapi_app/tests/ -v`.

## Today's Progress (2026-05-12)
- Fixed Supabase database schema consistency across SQLAlchemy models, setup scripts, and Supabase SQL
- Aligned column names and types in:
  - `/fastapi_app/app/models/extraction.py` (SQLAlchemy model)
  - `/fastapi_app/supabase_setup.sql` (Supabase setup script)
  - `/fastapi_app/app/db/setup.py` (database initialization script)
- Added missing columns: invoice_number, due_date, subtotal, tax
- Fixed user_id type consistency (Text with proper references)
- Ensured created_at/updated_at column naming consistency
- Made full_data column NOT NULL where appropriate
- Updated imports to remove unused dependencies
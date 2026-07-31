# Folder Structure

InvoiceIQ/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                         # FastAPI app entry point
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py                   # Application settings
│   │   │   └── database.py                 # DB engine & session
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── setup.py                   # Supabase table init script
│   │   │   └── verify_db.py                # DB verification helper
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── invoice.py                  # Pydantic models (LineItem, ExtractedInvoice, etc.)
│   │   │   ├── extraction.py               # SQLAlchemy extraction model
│   │   │   └── llm_config.py               # LLM configuration model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── extraction.py               # Response schema (ExtractionResponse)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── file_handler.py            # File validation & processing
│   │   │   ├── llm.py                     # Wrapper for provider selection
│   │   │   ├── llm_interface.py           # Base LLM service & concrete providers
│   │   │   ├── llm_config_service.py      # Service for LLM config CRUD
│   │   │   ├── parser.py                  # LLM response parsing & validation
│   │   │   └── db.py                      # Database service operations
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── extract.py             # POST/GET/PUT extraction endpoints
│   │   │       ├── history.py             # GET history endpoint
│   │   │       ├── export.py              # POST export endpoint (CSV/Excel)
│   │   │       └── llm_config.py          # LLM configuration endpoint
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                    # JWT validation with dev bypass
│   │   │   └── validators.py              # File validation helpers
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── api/
│   │       │   ├── __init__.py
│   │       │   └── test_extract.py
│   │       ├── models/
│   │       │   ├── __init__.py
│   │       │   └── test_invoice.py
│   │       └── services/
│   │           ├── __init__.py
│   │           └── test_parser.py
│   ├── alembic/
│   │   ├── env.py
│   │   ├── README
│   │   ├── versions/
│   │   │   └── [... migration files ...]
│   │   └── script.py.mako
│   ├── requirements.txt
│   └── .venv/
├── frontend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── page.tsx                     # Upload landing page
│   │   ├── login/
│   │   │   └── page.tsx                 # Login page
│   │   ├── llm-config/
│   │   │   └── page.tsx                 # LLM configuration page
│   │   ├── not-found.tsx                # 404 page
│   │   ├── error.tsx                    # Error page
│   │   ├── loading.tsx                  # Loading page
│   │   ├── history/
│   │   │   ├── __init__.py
│   │   │   └── page.tsx                 # History view
│   │   └── result/
│   │       ├── __init__.py
│   │       └── page.tsx                 # Result display & edit page
│   ├── middleware.ts                    # Auth middleware
│   ├── components/
│   │   ├── __init__.py
│   │   ├── Uploader.tsx                 # Drag‑and‑drop file upload component
│   │   ├── DataTable.tsx                # Editable invoice data table
│   │   ├── ExportButtons.tsx            # CSV/Excel export buttons
│   │   └── ui/
│   │       ├── __init__.py
│   │       └── button.tsx               # UI button primitive
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── postcss.config.js
├── .env.example
├── .env
├── CLAUDE.md
├── FOLDER_STRUCTURE.md
├── IMPLEMENTATION_SUMMARY.md
├── TASK_COMPLETION_SUMMARY.md
├── requirements.txt
└── scripts/
    ├── __init__.py
    └── download_models.py               # Script to download AI models

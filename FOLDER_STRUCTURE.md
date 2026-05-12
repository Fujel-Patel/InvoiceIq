# Folder Structure

InvoiceIQ/
├── fastapi_app/                              # Backend FastAPI Application
│   ├── app/                                  # Main Application Package
│   │   ├── __init__.py
│   │   ├── main.py                           # FastAPI app entry point
│   │   ├── core/                             # Core configuration and utilities
│   │   │   ├── __init__.py
│   │   │   ├── config.py                     # Application settings
│   │   │   └── database.py                   # Database setup and session management
│   │   ├── db/                               # Database models and base classes
│   │   │   ├── __init__.py
│   │   │   └── base.py                       # Base class for declarative models
│   │   ├── models/                           # Pydantic models for data validation
│   │   │   ├── __init__.py
│   │   │   └── invoice.py                    # Invoice-related Pydantic models
│   │   ├── schemas/                          # Request/response validation schemas
│   │   │   └── __init__.py
│   │   ├── services/                         # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── file_handler.py               # File validation and processing
│   │   │   ├── llm.py                        # Claude API integration
│   │   │   ├── parser.py                     # LLM response parsing and validation
│   │   │   └── db.py                         # Database service operations
│   │   ├── api/                              # API route definitions
│   │   │   ├── __init__.py
│   │   │   └── v1/                           # Version 1 API endpoints
│   │   │       ├── __init__.py
│   │   │       ├── extract.py                # File upload and data extraction
│   │   │       ├── history.py                # Extraction history management
│   │   │       └── export.py                 # Data export (CSV/Excel)
│   │   ├── tests/                            # Test suite
│   │   │   ├── __init__.py
│   │   │   ├── api/                          # API endpoint tests
│   │   │   │   ├── __init__.py
│   │   │   │   └── test_extract.py
│   │   │   ├── models/                       # Model validation tests
│   │   │   │   ├── __init__.py
│   │   │   │   └── test_invoice.py
│   │   │   └── services/                     # Service tests
│   │   │       ├── __init__.py
│   │   │       └── test_parser.py
│   │   └── utils/                            # Utility functions
│   │       ├── __init__.py
│   │       └── validators.py                 # File validation helpers
│   ├── alembic/                              # Database migration scripts
│   │   ├── env.py
│   │   ├── README
│   │   ├── versions/
│   │   │   └── [... migration files ...]
│   │   └── script.py.mako
│   ├── requirements.txt                      # Python backend dependencies
│   └── .venv/                                # Python virtual environment
├── frontend/                                 # Frontend Next.js Application
│   ├── app/                                  # Next.js App Router
│   │   ├── __init__.py
│   │   ├── page.tsx                          # Upload page for invoice/receipt files
│   │   ├── history/                          # History route
│   │   │   ├── __init__.py
│   │   │   └── page.tsx                      # View past extraction history
│   │   └── result/                           # Result route
│   │       ├── __init__.py
│   │       └── page.tsx                      # Display and edit extracted data
│   ├── components/                           # Reusable UI Components
│   │   ├── __init__.py
│   │   ├── Uploader.tsx                      # Drag & drop file upload component
│   │   ├── DataTable.tsx                     # Editable table for displaying data
│   │   ├── ExportButtons.tsx                 # CSV/Excel export buttons
│   │   └── ui/                               # UI primitives
│   │       ├── __init__.py
│   │       └── button.tsx                    # Button component
│   ├── package.json                          # Frontend dependencies
│   ├── tsconfig.json                         # TypeScript configuration
│   ├── tailwind.config.js                    # Tailwind CSS configuration
│   └── postcss.config.js                     # PostCSS configuration
├── .env.example                              # Example environment variables
├── .env                                      # Environment variables (local)
├── CLAUDE.md                                 # Claude Code guidance
├── FOLDER_STRUCTURE.md                       # This file
├── IMPLEMENTATION_SUMMARY.md                 # Summary of today's implementation
├── requirements.txt                          # Python dependencies (root level)
└── scripts/                                  # Utility scripts
    ├── __init__.py
    └── download_models.py                    # Script to download AI models
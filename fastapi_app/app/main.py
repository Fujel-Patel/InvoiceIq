from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import extract, history, export, llm_config
from .core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    extract.router,
    prefix=settings.API_V1_STR,
    tags=["extract"]
)
app.include_router(
    history.router,
    prefix=settings.API_V1_STR,
    tags=["history"]
)
app.include_router(
    export.router,
    prefix=settings.API_V1_STR,
    tags=["export"]
)
app.include_router(
    llm_config.router,
    prefix=settings.API_V1_STR,
    tags=["llm-config"]
)


@app.on_event("startup")
async def startup_event():
    """
    Run database setup on application startup.
    """
        # success = setup.setup_database()
    # Tables are already created manually, so we will skip this call.
    # If you need to run setup_database uncomment the line above and ensure Supabase is properly configured.


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
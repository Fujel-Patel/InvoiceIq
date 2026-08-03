from __future__ import annotations

import os
import sys
import time

# Ensure the repository root is importable when the app is started from inside
# the backend/ directory (e.g. `uvicorn app.main:app` on Render).
# Absolute imports (`from backend.app...`) are used throughout this project.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from fastapi import FastAPI, Request  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from loguru import logger  # noqa: E402

from .api.v1 import analytics, auth, extract, history, export, llm_config  # noqa: E402
from .core.config import settings  # noqa: E402
from .core.logging import setup_logging  # noqa: E402
from .routes import settings as settings_routes  # noqa: E402

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({elapsed_ms:.1f}ms)")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Include routers
app.include_router(
    auth.router,
    prefix=settings.API_V1_STR,
    tags=["auth"]
)
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
    analytics.router,
    prefix=settings.API_V1_STR,
    tags=["analytics"]
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
app.include_router(
    settings_routes.router,
    prefix="/settings",
    tags=["settings"]
)


@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.PROJECT_NAME}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

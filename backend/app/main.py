from __future__ import annotations

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .api.v1 import analytics, auth, extract, history, export, llm_config
from .core.config import settings
from .core.logging import setup_logging
from .routes import settings as settings_routes

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

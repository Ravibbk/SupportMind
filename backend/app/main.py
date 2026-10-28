"""SupportMind FastAPI Application Entry Point.

Configures CORS, middleware, lifecycle events, and routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI Customer Support Copilot for NovaCart with RAG, Agentic Routing, and Guardrails.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup CORS for Frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint for deployments and monitoring."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "demo_mode": settings.DEMO_MODE,
    }


@app.get("/", tags=["Root"])
async def root():
    """Root landing endpoint."""
    return {
        "message": "Welcome to SupportMind API. Visit /docs for OpenAPI documentation.",
        "version": settings.VERSION,
    }

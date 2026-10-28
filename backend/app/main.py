import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.config import settings
from app.db.seed import seed_orders

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler: seeds SQLite database on application startup."""
    try:
        count = seed_orders()
        logger.info("Successfully verified and seeded %d orders into database.", count)
    except Exception as e:
        logger.warning("Startup database initialization encountered an error: %s", e)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI Customer Support Copilot for NovaCart with RAG, Agentic Routing, and Guardrails.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Setup CORS for Frontend integration
cors_origins = settings.ALLOWED_ORIGINS if isinstance(settings.ALLOWED_ORIGINS, list) else [str(settings.ALLOWED_ORIGINS)]
is_wildcard = "*" in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=not is_wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API routes
app.include_router(api_router)


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


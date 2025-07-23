import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.database import engine, Base
from app.api.routes import customers, tags, notes, gdpr
from app.core.limiter import limiter

# Initialize structured logging before anything else
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Configure CORS
cors_origins = settings.CORS_ORIGINS
if isinstance(cors_origins, str):
    cors_origins = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(tags.router, prefix="/api/customers/tags", tags=["tags"])
app.include_router(tags.customer_router, prefix="/api/customers", tags=["tags"])
app.include_router(notes.customer_router, prefix="/api/customers", tags=["notes"])
app.include_router(gdpr.router, prefix="/api/gdpr", tags=["gdpr"])

# Initialize Prometheus metrics instrumentation
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/", tags=["root"])
async def root() -> dict:
    return {
        "message": "Welcome to BeeConect Customer Service API",
        "version": settings.PROJECT_VERSION,
        "docs_url": "/docs",
    }


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

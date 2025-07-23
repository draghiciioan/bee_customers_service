import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.db.database import engine, Base
from app.api.routes import customers, tags, notes, gdpr
from app.core.limiter import limiter

# Create tables in the database
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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

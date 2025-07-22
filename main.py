import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import engine, Base
from app.api.routes import customers, tags, notes, gdpr

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
)

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

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to BeeConect Customer Service API",
        "version": settings.PROJECT_VERSION,
        "docs_url": "/docs",
    }

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
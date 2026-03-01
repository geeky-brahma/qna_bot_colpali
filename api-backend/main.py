"""
FastAPI main application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from config import settings
from routes import router
from cache import cache
from inference import inference_backend
from models import HealthResponse
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    pinecone_ok = await cache.health_check()
    inference_ok = await inference_backend.health_check()
    
    return HealthResponse(
        status="healthy" if (pinecone_ok or inference_ok) else "degraded",
        timestamp=datetime.utcnow(),
        pinecone_connected=pinecone_ok
    )

@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    logger.info("✓ API Backend started")
    logger.info(f"Pinecone cache available: {cache.is_available()}")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    logger.info("API Backend shutting down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

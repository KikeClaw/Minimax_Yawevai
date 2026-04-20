"""
YAWEB.AI Backend - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

from .config import settings
from .routers import generate, webs, scraper, prospects, whatsapp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="YAWEB.AI API",
    description="API for generating static websites for local businesses using AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (note: scraper/prospects/whatsapp already have /api prefix)
app.include_router(generate.router, prefix="/api")
app.include_router(webs.router, prefix="/api")
app.include_router(scraper.router)  # Already has /api/scraper prefix
app.include_router(prospects.router)  # Already has /api/prospects prefix
app.include_router(whatsapp.router)  # Already has /api/whatsapp prefix

# Mount static files for previews
output_dir = Path(settings.output_dir)
output_dir.mkdir(parents=True, exist_ok=True)
app.mount("/preview", StaticFiles(directory=str(output_dir)), name="preview")


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "YAWEB.AI API",
        "version": "1.0.0",
        "description": "Generate static websites for local businesses using AI",
        "docs": "/docs",
        "endpoints": {
            "generate": "/api/generate",
            "list_webs": "/api/webs",
            "scraper": "/api/scraper/scan",
            "prospects": "/api/prospects",
            "whatsapp": "/api/whatsapp/send-batch",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "yaweb-ai-backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

"""
Generate Router - API endpoints for web generation
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid
import logging

from ..models import GenerationRequest, GenerationResponse, GeneratedWeb, WebListItem, WebListResponse
from ..services.google_scraper import google_scraper
from ..services.content_generator import content_generator
from ..services.web_builder import web_builder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generate", tags=["generation"])

# In-memory storage for demo (replace with database in production)
generated_webs = {}


@router.post("", response_model=GenerationResponse)
async def generate_web(request: GenerationRequest):
    """
    Generate a static website from Google Business URL and/or context
    """
    web_id = str(uuid.uuid4())[:8]
    
    try:
        # Step 1: Extract data from Google Business (if URL provided)
        google_data = None
        if request.google_url and request.google_url.strip():
            logger.info(f"Extracting data from Google Business: {request.google_url}")
            google_data = await google_scraper.extract(request.google_url)
        
        # Step 2: Generate content with AI
        logger.info("Generating content with AI...")
        generated_content = await content_generator.generate(google_data, request.context)
        
        # Step 3: Build the static website
        logger.info(f"Building website for web_id: {web_id}")
        build_result = await web_builder.build(generated_content, google_data, web_id)
        
        # Store the generated web
        web_name = google_data.name if google_data else request.context[:30].split('\n')[0]
        generated_webs[web_id] = GeneratedWeb(
            id=web_id,
            name=web_name,
            category="restaurante" if generated_content.is_restaurant_bar else "negocio local",
            plan=request.plan,
            google_url=request.google_url,
            context=request.context,
            extracted_data=google_data,
            generated_content=generated_content,
            files=[{"path": build_result["html_path"], "filename": "index.html", "size": 0}],
            preview_url=build_result["preview_url"],
            download_url=f"/api/download/{web_id}",
            created_at=datetime.now(),
            status="completed"
        )
        
        return GenerationResponse(
            success=True,
            web_id=web_id,
            preview_url=f"/preview/{web_id}",
            download_url=f"/api/download/{web_id}",
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error generating web: {e}")
        return GenerationResponse(
            success=False,
            error=str(e)
        )


@router.get("/status/{web_id}")
async def get_generation_status(web_id: str):
    """Get the status of a generated web"""
    if web_id in generated_webs:
        web = generated_webs[web_id]
        return {
            "web_id": web_id,
            "status": web.status,
            "name": web.name,
            "created_at": web.created_at.isoformat(),
            "preview_url": web.preview_url,
            "download_url": web.download_url
        }
    return {"web_id": web_id, "status": "not_found"}


@router.delete("/{web_id}")
async def delete_web(web_id: str):
    """Delete a generated web"""
    if web_id in generated_webs:
        del generated_webs[web_id]
        return {"success": True, "message": f"Web {web_id} deleted"}
    raise HTTPException(status_code=404, detail="Web not found")

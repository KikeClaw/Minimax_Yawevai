"""
Webs Router - API endpoints for managing generated webs
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import logging

from ..models import WebListResponse, WebListItem
from .generate import generated_webs

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webs", tags=["webs"])

# Get output directory from config
from ..config import settings


@router.get("", response_model=WebListResponse)
async def list_webs():
    """List all generated webs"""
    webs = [
        WebListItem(
            id=web.id,
            name=web.name,
            category=web.category,
            plan=web.plan,
            created_at=web.created_at.isoformat(),
            preview_url=web.preview_url,
            status=web.status
        )
        for web in generated_webs.values()
    ]
    return WebListResponse(webs=webs)


@router.get("/{web_id}")
async def get_web(web_id: str):
    """Get details of a specific web"""
    if web_id not in generated_webs:
        raise HTTPException(status_code=404, detail="Web not found")
    
    web = generated_webs[web_id]
    return {
        "id": web.id,
        "name": web.name,
        "category": web.category,
        "plan": web.plan.value,
        "google_url": web.google_url,
        "context": web.context,
        "status": web.status,
        "created_at": web.created_at.isoformat(),
        "preview_url": web.preview_url,
        "download_url": web.download_url,
        "content": web.generated_content.model_dump() if web.generated_content else None
    }


@router.get("/{web_id}/download")
async def download_web(web_id: str):
    """Download the web as a ZIP file"""
    if web_id not in generated_webs:
        raise HTTPException(status_code=404, detail="Web not found")
    
    zip_path = Path(settings.output_dir) / f"{web_id}.zip"
    
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="ZIP file not found")
    
    return FileResponse(
        path=str(zip_path),
        filename=f"{generated_webs[web_id].name.replace(' ', '-')}.zip",
        media_type="application/zip"
    )


@router.get("/{web_id}/preview")
async def preview_web(web_id: str):
    """Preview the generated web as HTML"""
    if web_id not in generated_webs:
        raise HTTPException(status_code=404, detail="Web not found")
    
    html_path = Path(settings.output_dir) / web_id / "index.html"
    
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="HTML file not found")
    
    return FileResponse(
        path=str(html_path),
        media_type="text/html"
    )


@router.delete("/{web_id}")
async def delete_web(web_id: str):
    """Delete a generated web"""
    if web_id not in generated_webs:
        raise HTTPException(status_code=404, detail="Web not found")
    
    # Delete files
    web_dir = Path(settings.output_dir) / web_id
    zip_path = Path(settings.output_dir) / f"{web_id}.zip"
    
    if web_dir.exists():
        import shutil
        shutil.rmtree(web_dir)
    
    if zip_path.exists():
        zip_path.unlink()
    
    # Remove from memory
    del generated_webs[web_id]
    
    return {"success": True, "message": f"Web {web_id} deleted"}

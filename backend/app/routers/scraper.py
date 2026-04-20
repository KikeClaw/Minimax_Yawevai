"""
Scraper Router - API endpoints for finding local businesses
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from ..services.scraper import GooglePlacesScraper, Prospect

router = APIRouter(prefix="/api/scraper", tags=["scraper"])

# In-memory storage for prospects (replace with DB later)
prospects_db: dict[str, Prospect] = {}

class ScanRequest(BaseModel):
    ciudad: str
    categoria: str = "restaurante"
    cantidad: int = 200

class ScanResponse(BaseModel):
    prospectos_encontrados: int
    prospectos_sin_web: int
    guardados: int

class BatchGenerateRequest(BaseModel):
    prospecto_ids: List[str]
    enviar_whatsapp: bool = False

@router.post("/scan", response_model=ScanResponse)
async def scan_businesses(request: ScanRequest):
    """Buscar negocios en una ciudad"""
    scraper = GooglePlacesScraper()

    # Search businesses
    businesses = await scraper.search_businesses(
        request.ciudad,
        request.categoria,
        request.cantidad
    )

    # Filter those without website
    without_web = scraper.filter_without_website(businesses)

    # Convert to prospects and save
    prospects = scraper.businesses_to_prospects(
        without_web,
        request.ciudad,
        request.categoria
    )

    for p in prospects:
        prospects_db[p.id] = p

    return ScanResponse(
        prospectos_encontrados=len(businesses),
        prospectos_sin_web=len(without_web),
        guardados=len(prospects)
    )

@router.get("/prospects", response_model=List[dict])
async def list_prospects():
    """Listar todos los prospectos"""
    return [
        {**p.model_dump(), "demo_url": f"demo.yawweb.ai/{p.slug}" if p.slug else None}
        for p in prospects_db.values()
    ]

@router.post("/generate-batch")
async def generate_batch(request: BatchGenerateRequest):
    """Generar demos para una lista de prospectos"""
    from .generate import web_builder, content_generator

    results = []
    for pid in request.prospecto_ids:
        if pid not in prospects_db:
            continue

        prospect = prospects_db[pid]

        # Generate web using existing services
        # TODO: implement full generation

        results.append({
            "prospect_id": pid,
            "slug": prospect.slug,
            "demo_url": f"demo.yawweb.ai/{prospect.slug}"
        })

    return {"generated": len(results), "results": results}

@router.delete("/prospects/{prospect_id}")
async def delete_prospect(prospect_id: str):
    """Eliminar un prospecto"""
    if prospect_id not in prospects_db:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")

    del prospects_db[prospect_id]
    return {"success": True, "message": f"Prospecto {prospect_id} eliminado"}

# Export for other routers
def get_prospects_db() -> dict[str, Prospect]:
    return prospects_db
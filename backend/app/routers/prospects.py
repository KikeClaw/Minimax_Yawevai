"""
Prospects Router - API endpoints for managing prospects
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

# Import from scraper router (shared db)
from .scraper import prospects_db, router as base_router

router = APIRouter(prefix="/api/prospects", tags=["prospects"])

class ProspectUpdate(BaseModel):
    estado: Optional[Literal["prospect", "demo", "sent", "interested", "active"]] = None
    telefono: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None

@router.get("")
async def list_prospects():
    """Listar todos los prospectos"""
    return [
        {**p.model_dump(), "demo_url": f"demo.yawweb.ai/{p.slug}" if p.slug else None}
        for p in prospects_db.values()
    ]

@router.get("/{prospect_id}")
async def get_prospect(prospect_id: str):
    """Obtener detalle de un prospecto"""
    if prospect_id not in prospects_db:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")

    prospect = prospects_db[prospect_id]
    return {
        **prospect.model_dump(),
        "demo_url": f"demo.yawweb.ai/{prospect.slug}" if prospect.slug else None
    }

@router.patch("/{prospect_id}")
async def update_prospect(prospect_id: str, update: ProspectUpdate):
    """Actualizar estado de un prospecto"""
    if prospect_id not in prospects_db:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")

    prospect = prospects_db[prospect_id]

    if update.estado:
        prospect.estado = update.estado
    if update.telefono:
        prospect.telefono = update.telefono
    if update.whatsapp:
        prospect.whatsapp = update.whatsapp
    if update.email:
        prospect.email = update.email

    prospect.updated_at = datetime.now()

    return {"success": True, "prospect": prospect.model_dump()}

@router.delete("/{prospect_id}")
async def delete_prospect(prospect_id: str):
    """Eliminar un prospecto"""
    if prospect_id not in prospects_db:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")

    del prospects_db[prospect_id]
    return {"success": True}
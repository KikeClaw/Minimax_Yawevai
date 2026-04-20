"""
WhatsApp Router - API endpoints for bulk messaging
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from ..services.whatsapp_service import WhatsAppService
from ..services.whatsapp_service import Prospect as WhatsAppProspect

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])

whatsapp_service = WhatsAppService()

class SendBatchRequest(BaseModel):
    prospecto_ids: List[str]
    template: str = "hola"  # "hola" or "seguimiento"

class MessagePreview(BaseModel):
    prospect_id: str
    telefono: str
    mensaje: str

@router.get("/templates")
async def list_templates():
    """Listar templates disponibles"""
    return {
        "templates": [
            {"name": "hola", "description": "Mensaje inicial con link demo"},
            {"name": "seguimiento", "description": "Mensaje de seguimiento"}
        ]
    }

@router.post("/preview")
async def preview_messages(request: SendBatchRequest):
    """Previsualizar mensajes antes de enviar"""
    from .scraper import prospects_db

    messages = []
    for pid in request.prospecto_ids:
        if pid not in prospects_db:
            continue

        prospect = prospects_db[pid]
        mensaje = whatsapp_service.generate_message(prospect, request.template)

        messages.append(MessagePreview(
            prospect_id=pid,
            telefono=prospect.telefono or prospect.whatsapp or "",
            mensaje=mensaje
        ))

    return {"messages": messages}

@router.post("/send-batch")
async def send_batch(request: SendBatchRequest):
    """Enviar mensajes masivos por WhatsApp"""
    from .scraper import prospects_db

    # Get prospects
    prospects_list = [
        prospects_db[pid] for pid in request.prospecto_ids
        if pid in prospects_db
    ]

    if not prospects_list:
        raise HTTPException(status_code=400, detail="No se encontraron prospectos")

    # Send batch
    result = whatsapp_service.send_batch(prospects_list, request.template)

    # Update prospect status to "sent"
    for pid in request.prospecto_ids:
        if pid in prospects_db:
            prospects_db[pid].estado = "sent"

    return {
        "success": True,
        "sent": result.sent,
        "failed": result.failed,
        "message": f"Enviados {result.sent} mensajes, {result.failed} fallidos"
    }

@router.get("/status")
async def get_status():
    """Obtener estado del servicio WhatsApp"""
    return {
        "configured": whatsapp_service.is_configured(),
        "rate_limit": {
            "max_per_hour": whatsapp_service.rate_limiter.max_per_hour,
            "remaining": whatsapp_service.rate_limiter.get_remaining(),
            "resets_at": whatsapp_service.rate_limiter.get_reset_time()
        }
    }
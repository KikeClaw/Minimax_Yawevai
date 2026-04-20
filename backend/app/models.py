from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class PlanType(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    LAN_PLUS = "lan_plus"


class GenerationRequest(BaseModel):
    google_url: Optional[str] = Field(None, description="URL de Google Business Profile")
    context: str = Field(..., min_length=1, description="Contexto adicional para la IA")
    plan: PlanType = PlanType.BASIC


class GoogleBusinessData(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    hours: Optional[Dict[str, str]] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    photos: List[str] = []
    website: Optional[str] = None
    social_links: Dict[str, Optional[str]] = {}
    menu_url: Optional[str] = None
    is_restaurant: bool = False
    place_id: Optional[str] = None


class GeneratedContent(BaseModel):
    title: str
    subtitle: str
    about_text: str
    services: List[str]
    cta_text: str
    primary_color: str
    opening_hours_html: str
    seo_title: str
    seo_description: str
    social_links: Dict[str, Optional[str]]
    menu_pdf_url: Optional[str] = None
    is_restaurant_bar: bool = False


class WebFile(BaseModel):
    path: str
    filename: str
    size: int


class GeneratedWeb(BaseModel):
    id: str
    name: str
    category: str
    plan: PlanType
    google_url: Optional[str] = None
    context: str
    extracted_data: Optional[GoogleBusinessData] = None
    generated_content: Optional[GeneratedContent] = None
    files: List[WebFile] = []
    preview_url: Optional[str] = None
    download_url: Optional[str] = None
    created_at: datetime
    status: str = "processing"


class GenerationResponse(BaseModel):
    success: bool
    web_id: Optional[str] = None
    preview_url: Optional[str] = None
    download_url: Optional[str] = None
    generated_at: Optional[str] = None
    error: Optional[str] = None


class WebListItem(BaseModel):
    id: str
    name: str
    category: str
    plan: PlanType
    created_at: str
    preview_url: Optional[str] = None
    status: str


class WebListResponse(BaseModel):
    webs: List[WebListItem]

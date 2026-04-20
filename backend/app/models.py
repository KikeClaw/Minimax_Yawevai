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


# AI Provider Models
class AIProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MINIMAX = "minimax"
    MOCK = "mock"


class AIModel(BaseModel):
    id: str
    name: str
    provider: AIProvider
    description: str = ""
    max_tokens: int = 4096
    supports_vision: bool = False
    supports_json: bool = True


class AIConfig(BaseModel):
    provider: AIProvider = AIProvider.OPENAI
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000


class AIConfigUpdate(BaseModel):
    provider: Optional[AIProvider] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


# Available models per provider
AVAILABLE_MODELS = {
    AIProvider.OPENAI: [
        AIModel(id="gpt-4o", name="GPT-4o", provider=AIProvider.OPENAI, description="Best overall, fast", supports_vision=True, supports_json=True),
        AIModel(id="gpt-4o-mini", name="GPT-4o Mini", provider=AIProvider.OPENAI, description="Fast & affordable", supports_vision=True, supports_json=True),
        AIModel(id="gpt-4-turbo", name="GPT-4 Turbo", provider=AIProvider.OPENAI, description="Previous best model", max_tokens=128000, supports_vision=True),
    ],
    AIProvider.ANTHROPIC: [
        AIModel(id="claude-3-5-sonnet-20241022", name="Claude 3.5 Sonnet", provider=AIProvider.ANTHROPIC, description="Best reasoning, excellent quality", max_tokens=8192, supports_vision=True),
        AIModel(id="claude-3-opus", name="Claude 3 Opus", provider=AIProvider.ANTHROPIC, description="Most capable, slower", max_tokens=4096, supports_vision=True),
        AIModel(id="claude-3-haiku", name="Claude 3 Haiku", provider=AIProvider.ANTHROPIC, description="Fast & affordable", max_tokens=4096, supports_vision=True),
    ],
    AIProvider.GOOGLE: [
        AIModel(id="gemini-1.5-pro", name="Gemini 1.5 Pro", provider=AIProvider.GOOGLE, description="Long context, multimodal", max_tokens=32768, supports_vision=True, supports_json=True),
        AIModel(id="gemini-1.5-flash", name="Gemini 1.5 Flash", provider=AIProvider.GOOGLE, description="Fast & efficient", max_tokens=32768, supports_vision=True, supports_json=True),
        AIModel(id="gemini-1.5-flash-8b", name="Gemini 1.5 Flash-8B", provider=AIProvider.GOOGLE, description="Fastest & cheapest", max_tokens=32768, supports_vision=True, supports_json=True),
    ],
    AIProvider.MINIMAX: [
        AIModel(id="abab6.5s-chat", name="ABAB 6.5S Chat", provider=AIProvider.MINIMAX, description="Fast Chinese-optimized", max_tokens=245760, supports_json=True),
        AIModel(id="abab6-chat", name="ABAB 6 Chat", provider=AIProvider.MINIMAX, description="Balanced performance", max_tokens=245760, supports_json=True),
        AIModel(id="gemma-2-27b-chat", name="Gemma 2 27B", provider=AIProvider.MINIMAX, description="Open source optimized", max_tokens=8192, supports_json=True),
    ],
    AIProvider.MOCK: [
        AIModel(id="mock", name="Mock (No API)", provider=AIProvider.MOCK, description="Template-based generation", supports_json=True),
    ],
}

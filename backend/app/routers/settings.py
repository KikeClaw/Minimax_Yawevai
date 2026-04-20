"""
Settings Router - AI Configuration endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..models import AIConfig, AIConfigUpdate, AIProvider, AIModel, AVAILABLE_MODELS
from ..config import settings
import json
import os

router = APIRouter(prefix="/api/settings", tags=["settings"])

SETTINGS_FILE = "./ai_settings.json"


def load_settings() -> Dict[str, Any]:
    """Load AI settings from file"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "provider": settings.llm_provider,
        "model": settings.llm_model,
        "api_keys": {
            "openai": settings.openai_api_key or "",
            "anthropic": settings.anthropic_api_key or "",
            "google": settings.google_api_key or "",
            "minimax": settings.minimax_api_key or "",
        },
        "temperature": 0.7,
        "max_tokens": 2000,
    }


def save_settings(config: Dict[str, Any]) -> None:
    """Save AI settings to file"""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(config, f, indent=2)


@router.get("/ai")
async def get_ai_config() -> AIConfig:
    """Get current AI configuration"""
    config = load_settings()
    return AIConfig(
        provider=AIProvider(config.get("provider", "mock")),
        model=config.get("model", "gpt-4o"),
        api_key=None,  # Never expose API keys
        temperature=config.get("temperature", 0.7),
        max_tokens=config.get("max_tokens", 2000),
    )


@router.put("/ai")
async def update_ai_config(update: AIConfigUpdate) -> AIConfig:
    """Update AI configuration"""
    config = load_settings()
    
    if update.provider is not None:
        config["provider"] = update.provider.value
        settings.llm_provider = update.provider.value
    
    if update.model is not None:
        config["model"] = update.model
        settings.llm_model = update.model
    
    if update.api_key is not None:
        # Save the new API key
        config["api_keys"][config["provider"]] = update.api_key
        
        # Update environment/config
        if config["provider"] == "openai":
            settings.openai_api_key = update.api_key
        elif config["provider"] == "anthropic":
            settings.anthropic_api_key = update.api_key
        elif config["provider"] == "google":
            settings.google_api_key = update.api_key
        elif config["provider"] == "minimax":
            settings.minimax_api_key = update.api_key
    
    if update.temperature is not None:
        config["temperature"] = update.temperature
    
    if update.max_tokens is not None:
        config["max_tokens"] = update.max_tokens
    
    save_settings(config)
    
    return AIConfig(
        provider=AIProvider(config["provider"]),
        model=config["model"],
        api_key=None,  # Never expose API keys
        temperature=config["temperature"],
        max_tokens=config["max_tokens"],
    )


@router.get("/ai/providers")
async def get_providers() -> List[Dict[str, Any]]:
    """Get available AI providers with their models"""
    providers = []
    for provider, models in AVAILABLE_MODELS.items():
        # Check if provider has API key configured
        has_key = False
        if provider == AIProvider.OPENAI and settings.openai_api_key:
            has_key = True
        elif provider == AIProvider.ANTHROPIC and settings.anthropic_api_key:
            has_key = True
        elif provider == AIProvider.GOOGLE and settings.google_api_key:
            has_key = True
        elif provider == AIProvider.MINIMAX and settings.minimax_api_key:
            has_key = True
        elif provider == AIProvider.MOCK:
            has_key = True
        
        providers.append({
            "id": provider.value,
            "name": _get_provider_name(provider),
            "has_api_key": has_key,
            "models": [
                {
                    "id": m.id,
                    "name": m.name,
                    "description": m.description,
                    "supports_vision": m.supports_vision,
                }
                for m in models
            ],
        })
    return providers


@router.get("/ai/models")
async def get_models_for_provider(provider: AIProvider) -> List[AIModel]:
    """Get available models for a specific provider"""
    if provider not in AVAILABLE_MODELS:
        raise HTTPException(status_code=404, detail="Provider not found")
    return AVAILABLE_MODELS[provider]


def _get_provider_name(provider: AIProvider) -> str:
    """Get display name for provider"""
    names = {
        AIProvider.OPENAI: "OpenAI",
        AIProvider.ANTHROPIC: "Anthropic Claude",
        AIProvider.GOOGLE: "Google Gemini",
        AIProvider.MINIMAX: "MiniMax",
        AIProvider.MOCK: "Mock (Free)",
    }
    return names.get(provider, provider.value)


@router.post("/ai/test")
async def test_ai_connection(config: AIConfig) -> Dict[str, Any]:
    """Test AI connection with provided config"""
    try:
        # Simple test - try to generate a short response
        from ..services.content_generator import content_generator
        
        # Temporarily update settings for testing
        old_provider = settings.llm_provider
        old_model = settings.llm_model
        
        settings.llm_provider = config.provider.value
        settings.llm_model = config.model
        
        if config.api_key:
            if config.provider == AIProvider.OPENAI:
                settings.openai_api_key = config.api_key
            elif config.provider == AIProvider.ANTHROPIC:
                settings.anthropic_api_key = config.api_key
            elif config.provider == AIProvider.GOOGLE:
                settings.google_api_key = config.api_key
            elif config.provider == AIProvider.MINIMAX:
                settings.minimax_api_key = config.api_key
        
        # Reinitialize the content generator
        content_generator.provider = config.provider.value
        content_generator.model = config.model
        content_generator._init_llm_client()
        
        # Try a simple generation
        result = await content_generator.generate(
            None,
            "Restaurante El Mar - Marisqueria en Valencia - Especialidad en paella"
        )
        
        # Restore settings
        settings.llm_provider = old_provider
        settings.llm_model = old_model
        
        return {
            "success": True,
            "message": f"Successfully connected to {config.provider.value}",
            "model_used": config.model,
            "generated_title": result.title,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }

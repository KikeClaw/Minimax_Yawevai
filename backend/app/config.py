from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # App settings
    app_name: str = "YAWEB.AI"
    debug: bool = True
    api_prefix: str = "/api"
    
    # LLM Settings - Multi-provider support
    llm_provider: str = "mock"  # "openai", "anthropic", "google", "minimax", "mock"
    llm_model: str = "gpt-4o"  # Default model
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    minimax_api_key: Optional[str] = None
    minimax_group_id: Optional[str] = None  # Required for Minimax API
    
    # Google Places
    google_places_api_key: Optional[str] = None
    use_playwright_scraper: bool = True
    
    # Paths
    output_dir: str = "./output"
    templates_dir: str = "./templates"
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

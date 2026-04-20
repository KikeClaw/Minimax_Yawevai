from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # App settings
    app_name: str = "YAWEB.AI"
    debug: bool = True
    api_prefix: str = "/api"
    
    # LLM Settings
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_provider: str = "openai"  # "openai", "anthropic", or "mock"
    
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

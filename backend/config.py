from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    transloc_api_key: str = "8882812681"
    transloc_base_url: str = "https://gatech.transloc.com/Services/JSONPRelay.svc"
    
    # CORS origins
    cors_origins: list = [
        "http://localhost:3000",
        "https://buzz-bus.vercel.app",
        "https://buzzbus.netlify.app",
        "https://buzzbus.vercel.app",
    ]
    
    # Server settings
    port: int = 5000
    host: str = "0.0.0.0"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # Ignore extra environment variables
    }


settings = Settings()


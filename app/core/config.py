from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List, Optional
import json

class Settings(BaseSettings):
    # App Settings
    app_name: str = "Truth Finder AI"
    app_version: str = "1.0.0"
    debug: bool = True

    # Twitter API credentials
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
    twitter_bearer_token: Optional[str] = None

    # Gemini, Supabase, etc.
    gemini_api_key: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    # CORS
    cors_origins: List[str] = ["https://truth-finder-ai.vercel.app", "http://localhost:3000"]

    # API Settings
    max_tweets_per_request: int = 50
    default_tweets_count: int = 10

    model_config = ConfigDict(
        env_file=".env",        # ✅ Load from .env
        extra="ignore"
    )

    @classmethod
    def parse_env_var(cls, field_name: str, raw_val: str):
        if field_name == 'cors_origins':
            return [origin.strip() for origin in raw_val.split(',') if origin.strip()]
        try:
            return json.loads(raw_val)
        except Exception:
            return raw_val

# Instantiate settings
settings = Settings()

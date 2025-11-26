from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Load environment variables from repo root and backend folder for convenience.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")


class Settings(BaseSettings):
    app_name: str = "Research Spider"
    semantic_scholar_api_key: Optional[str] = Field(
        default=None, alias="SEMANTIC_SCHOLAR_API_KEY"
    )
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    openalex_email: Optional[str] = Field(default=None, alias="OPENALEX_EMAIL")
    request_timeout: int = Field(default=15, alias="REQUEST_TIMEOUT_SECONDS")
    max_graph_nodes: int = Field(default=30, alias="MAX_GRAPH_NODES")
    max_graph_depth: int = Field(default=2, alias="MAX_GRAPH_DEPTH")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", populate_by_name=True, extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()

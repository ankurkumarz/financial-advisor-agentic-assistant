"""Configuration settings for the multi-agent system."""
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google Cloud
    google_cloud_project: str
    google_cloud_region: str = "us-central1"
    google_api_key: str

    # Vertex AI
    vertex_ai_location: str = "us-central1"
    vertex_ai_model: str = "gemini-2.5-flash"
    vertex_ai_research_model: str = "gemini-2.5-pro"
    vertex_ai_compliance_model: str = "gemini-2.5-flash"
    vertex_ai_memory_bank_id: Optional[str] = None
    vertex_ai_session_service_endpoint: Optional[str] = None

    # Agent Configuration
    orchestrator_temperature: Optional[float] = 0.7
    planner_temperature: Optional[float] = 0.5
    retriever_temperature: Optional[float] = 0.3
    reviewer_temperature: Optional[float] = 0.2

    # Chroma DB
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "financial_documents"
    chroma_docs_folder: str = "./docs/pdfs"

    kaggle_api_token: Optional[str] = None
    crm_leads_dataset: Optional[str] = None

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Session & Memory
    session_storage: Optional[str] = "memory" 

    # Application
    max_retries: int = 3
    timeout_seconds: int = 30

    class Config:
        # Look for .env in multiple locations to support both:
        # 1. Running from project root (python -m app.main)
        # 2. Running with adk web from app/ directory
        env_file = (
            Path("app/.env"),     # When running from project root
            Path(".env"),         # When running from app/ (adk web)
            Path("../.env"),      # Fallback: parent directory
        )
        case_sensitive = False


settings = Settings()

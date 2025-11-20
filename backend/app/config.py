"""
Configuration management for mini_n8n
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    app_name: str = "mini_n8n"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database Settings
    database_url: str = "sqlite+aiosqlite:///./mini_n8n.db"
    
    # LLM Settings
    llm_provider: str = "openai"  # "openai" or "vertexai"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    
    # Vertex AI Settings
    vertexai_project_id: Optional[str] = None
    vertexai_location: str = "us-central1"
    vertexai_model: str = "gemini-pro"
    
    # Workflow Settings
    max_workflow_execution_time: int = 3600  # seconds
    max_node_retries: int = 3
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()


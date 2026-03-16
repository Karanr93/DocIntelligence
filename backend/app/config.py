from pydantic import BaseSettings
from pathlib import Path
import os


class Settings(BaseSettings):
    # LLM
    openai_api_key: str = ""
    groq_api_key: str = ""
    llm_provider: str = "bedrock"  # "groq", "openai", or "bedrock"
    llm_model: str = "us.anthropic.claude-sonnet-4-20250514-v1:0"

    # Bedrock
    bedrock_region: str = "us-east-1"

    # Ollama (local)
    ollama_base_url: str = "http://localhost:11434/v1"

    # AWS
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    s3_bucket_name: str = "document-clause-system"

    # Database
    database_url: str = "sqlite:///./clause_system.db"

    # Directories
    upload_dir: str = "./uploaded_pdfs"
    annotated_dir: str = "./annotated_pdfs"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Ensure directories exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.annotated_dir, exist_ok=True)

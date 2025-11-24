import os
from typing import Literal
from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("BASE_API_KEY")
base_url = os.getenv("BASE_URL")
model_name =os.getenv("MODEL_NAME")
embedding_model= os.getenv("EMBEDDING_MODEL")

class Settings(BaseSettings):
    LOG_LEVEL: str = "INFO"

    API_KEY: SecretStr = Field(api_key, description="API Key for the Model Provider")
    
    
    BASE_URL: str = Field(base_url, description="API Endpoint")
    
    MODEL_NAME: str = Field(model_name, description="Main reasoning model")
    EMBEDDING_MODEL: str = Field(embedding_model, description="Embedding model for RAG")

    MAX_RETRIES: int = 3
    TIMEOUT_SECONDS: int = 60

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
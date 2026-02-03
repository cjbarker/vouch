"""Application configuration management."""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "vouch"

    # Elasticsearch Configuration
    elasticsearch_url: str = "http://localhost:9200"

    # Ollama Configuration
    ollama_api_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2-vision"

    # File Upload Configuration
    max_upload_size: int = 5242880  # 5MB in bytes
    upload_dir: Path = Path("./uploads")
    allowed_extensions: str = "jpg,jpeg,png,pdf"

    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get list of allowed file extensions."""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]

    def model_post_init(self, __context) -> None:
        """Create upload directory if it doesn't exist."""
        if isinstance(self.upload_dir, str):
            self.upload_dir = Path(self.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()

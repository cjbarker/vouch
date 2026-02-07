"""Tests for application configuration."""

from pathlib import Path

from app.config import LLMProvider, Settings


class TestLLMProvider:
    """Tests for LLMProvider enum."""

    def test_ollama_provider(self):
        """Test Ollama provider enum value."""
        assert LLMProvider.OLLAMA.value == "ollama"

    def test_openai_provider(self):
        """Test OpenAI provider enum value."""
        assert LLMProvider.OPENAI.value == "openai"

    def test_gemini_provider(self):
        """Test Gemini provider enum value."""
        assert LLMProvider.GEMINI.value == "gemini"

    def test_all_providers(self):
        """Test all provider values."""
        providers = list(LLMProvider)
        assert len(providers) == 3
        assert LLMProvider.OLLAMA in providers
        assert LLMProvider.OPENAI in providers
        assert LLMProvider.GEMINI in providers


class TestSettings:
    """Tests for Settings class."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        assert settings.mongodb_url == "mongodb://localhost:27017"
        assert settings.mongodb_db_name == "vouch"
        assert settings.elasticsearch_url == "http://localhost:9200"
        assert settings.llm_provider == LLMProvider.OLLAMA
        assert settings.ollama_api_url == "http://localhost:11434"
        assert settings.ollama_model == "llama3.2-vision"

    def test_ollama_configuration(self):
        """Test Ollama configuration."""
        settings = Settings()
        assert settings.ollama_api_url == "http://localhost:11434"
        assert settings.ollama_model == "llama3.2-vision"

    def test_openai_configuration(self):
        """Test OpenAI configuration."""
        settings = Settings()
        assert settings.openai_api_key is None
        assert settings.openai_model == "gpt-4-vision-preview"
        assert settings.openai_max_tokens == 4096
        assert settings.openai_temperature == 0.0

    def test_gemini_configuration(self):
        """Test Gemini configuration."""
        settings = Settings()
        assert settings.gemini_api_key is None
        assert settings.gemini_model == "gemini-1.5-pro-vision"
        assert settings.gemini_temperature == 0.0

    def test_file_upload_configuration(self):
        """Test file upload configuration."""
        settings = Settings()
        assert settings.max_upload_size == 5242880  # 5MB
        assert settings.upload_dir == Path("./uploads")
        assert settings.allowed_extensions == "jpg,jpeg,png,pdf"

    def test_allowed_extensions_list(self):
        """Test allowed extensions list property."""
        settings = Settings()
        extensions = settings.allowed_extensions_list
        assert len(extensions) == 4
        assert "jpg" in extensions
        assert "jpeg" in extensions
        assert "png" in extensions
        assert "pdf" in extensions

    def test_upload_dir_creation(self, tmp_path):
        """Test that upload directory is created."""
        upload_dir = tmp_path / "test_uploads"
        Settings(upload_dir=upload_dir)
        assert upload_dir.exists()
        assert upload_dir.is_dir()

    def test_custom_settings(self):
        """Test custom settings override defaults."""
        custom_settings = Settings(
            mongodb_url="mongodb://custom:27017",
            mongodb_db_name="custom_db",
            llm_provider=LLMProvider.OPENAI,
            openai_api_key="test_key",
        )
        assert custom_settings.mongodb_url == "mongodb://custom:27017"
        assert custom_settings.mongodb_db_name == "custom_db"
        assert custom_settings.llm_provider == LLMProvider.OPENAI
        assert custom_settings.openai_api_key == "test_key"

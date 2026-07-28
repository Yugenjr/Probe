"""System environment configuration loading."""
from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global configuration properties loaded via `.env` or system variables."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Platform Integration (No hardcoded credentials allowed)
    driftguard_base_url: str = Field(default="http://localhost:8000")
    driftguard_api_key: Optional[str] = Field(default=None)
    request_timeout_seconds: int = Field(default=30)

    # LLM Providers
    llm_provider: str = Field(default="openai", description="Active AI provider backend")
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    ollama_base_url: str = Field(default="http://localhost:11434")
    default_temperature: float = Field(default=0.1)

    # OpenTelemetry
    enable_telemetry: bool = Field(default=True)
    otlp_exporter_endpoint: str = Field(default="http://localhost:4317")
    telemetry_service_name: str = Field(default="driftguard-probe")

    # Server Configuration
    probe_port: int = Field(default=8001)
    probe_host: str = Field(default="0.0.0.0")
    debug_mode: bool = Field(default=False)


@lru_cache()
def get_settings() -> Settings:
    """Return singleton configuration settings instance."""
    return Settings()

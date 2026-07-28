"""System environment configuration loading."""
from functools import lru_cache
from typing import Optional
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global configuration properties loaded via `.env` or system variables."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Platform Integration (No hardcoded credentials allowed)
    driftguard_base_url: str = Field(
        default="http://localhost:8000",
        validation_alias=AliasChoices("DRIFTGUARD_API_URL", "DRIFTGUARD_BASE_URL", "driftguard_base_url")
    )
    driftguard_api_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("DRIFTGUARD_API_KEY", "driftguard_api_key")
    )
    request_timeout_seconds: int = Field(
        default=30,
        validation_alias=AliasChoices("DRIFTGUARD_TIMEOUT", "REQUEST_TIMEOUT_SECONDS", "request_timeout_seconds")
    )

    # LLM Providers
    llm_provider: str = Field(default="openai", description="Active AI provider backend")
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    groq_api_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("GROQ_API_KEY", "groq_api_key")
    )
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

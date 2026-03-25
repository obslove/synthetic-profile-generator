from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    simplelogin_api_key: str | None = Field(default=None, alias="SIMPLELOGIN_API_KEY")
    simplelogin_base_url: str = Field(
        default="https://api.simplelogin.io/api",
        alias="SIMPLELOGIN_BASE_URL",
    )
    request_timeout_seconds: float = Field(default=5.0, alias="REQUEST_TIMEOUT_SECONDS")
    fallback_email_domains: list[str] = Field(
        default_factory=lambda: ["example.com", "example.org", "example.net"],
        alias="FALLBACK_EMAIL_DOMAINS",
    )
    default_country_code: str = Field(default="US", alias="DEFAULT_COUNTRY_CODE")
    strict_identifier_safety_mode: bool = Field(
        default=True,
        alias="STRICT_IDENTIFIER_SAFETY_MODE",
    )

    @field_validator("fallback_email_domains", mode="before")
    @classmethod
    def parse_fallback_domains(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

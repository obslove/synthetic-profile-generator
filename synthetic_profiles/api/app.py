from __future__ import annotations

from fastapi import FastAPI

from synthetic_profiles.bootstrap import build_profile_generator
from synthetic_profiles.config.logging import configure_logging
from synthetic_profiles.config.settings import Settings
from synthetic_profiles.models.schemas import (
    BatchGenerationRequest,
    GenerationRequest,
)
from synthetic_profiles.services.country_registry import CountryRegistry
from synthetic_profiles.services.output_formatter import OutputFormatter

configure_logging()
settings = Settings()
app = FastAPI(title="Gerador de Perfis Sintéticos", version="0.1.0")
generator = build_profile_generator(settings)
registry = CountryRegistry()
formatter = OutputFormatter()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/countries")
async def countries() -> list[dict[str, str | bool]]:
    return registry.list_countries()


@app.post("/generate-profile")
async def generate_profile(request: GenerationRequest) -> dict[str, object]:
    profile = await generator.generate_profile(request)
    return formatter.format_profile(
        profile,
        debug=request.debug_output,
        legacy=request.response_mode.value == "legacy",
    )


@app.post("/generate-batch")
async def generate_batch(request: BatchGenerationRequest) -> dict[str, object]:
    response = await generator.generate_batch(request)
    return formatter.format_batch(
        response,
        debug=request.debug_output,
        legacy=request.response_mode.value == "legacy",
    )

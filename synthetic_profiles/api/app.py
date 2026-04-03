from __future__ import annotations

from fastapi import FastAPI, HTTPException

from synthetic_profiles.bootstrap import build_profile_generator
from synthetic_profiles.config.logging import configure_logging
from synthetic_profiles.config.settings import Settings
from synthetic_profiles.models.schemas import (
    BatchGenerationRequest,
    GenerationRequest,
)
from synthetic_profiles.services.country_registry import CountryRegistry
from synthetic_profiles.services.output_formatter import OutputFormatter
from synthetic_profiles.utils.exceptions import UnsupportedCountryError, UnsupportedSubdivisionError

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
async def countries() -> list[dict[str, str | bool | int | list[str] | None]]:
    return registry.list_countries()


@app.get("/countries/{country_code}/states")
async def states(country_code: str) -> list[dict[str, str]]:
    try:
        return registry.list_subdivisions(country_code.strip().upper())
    except UnsupportedCountryError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/countries/{country_code}/subdivisions/{subdivision_code}/cities")
async def cities(country_code: str, subdivision_code: str) -> list[dict[str, str | bool]]:
    try:
        return registry.list_cities(country_code.strip().upper(), subdivision_code.strip())
    except UnsupportedCountryError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except UnsupportedSubdivisionError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


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

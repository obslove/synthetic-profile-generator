from __future__ import annotations

import asyncio
import json
import logging
from typing import Annotated

import typer

from synthetic_profiles.bootstrap import build_profile_generator
from synthetic_profiles.config.logging import configure_logging
from synthetic_profiles.config.settings import Settings
from synthetic_profiles.models.enums import Gender, ResponseMode
from synthetic_profiles.models.schemas import BatchGenerationRequest, GenerationRequest
from synthetic_profiles.services.country_registry import CountryRegistry
from synthetic_profiles.services.output_formatter import OutputFormatter

configure_logging(level=logging.ERROR)
app = typer.Typer(help="CLI do gerador de perfis sintéticos.")
settings = Settings()
generator = build_profile_generator(settings)
registry = CountryRegistry()
formatter = OutputFormatter()


def _normalize_output_format(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in {"compact", "pretty"}:
        raise typer.BadParameter("o formato deve ser um destes: compact, pretty")
    return normalized


def _emit(data: object, output_format: str, *, debug: bool) -> None:
    if output_format == "pretty":
        typer.echo(formatter.to_pretty_text(data, debug=debug))
        return
    typer.echo(formatter.to_compact_text(data, debug=debug))


def _request_from_options(
    *,
    country: str,
    gender: Gender,
    age: int | None,
    password_length: int,
) -> dict[str, object]:
    age_min = age if age is not None else 16
    age_max = age if age is not None else 78
    return {
        "country_code": country,
        "gender": gender,
        "age_min": age_min,
        "age_max": age_max,
        "password_length": password_length,
        "use_simplelogin": True,
        "include_cpf": True,
        "seed": None,
        "debug_output": False,
        "response_mode": ResponseMode.CLEAN,
    }


@app.command("generate")
def generate(
    country: Annotated[str, typer.Option("--c")] = settings.default_country_code,
    gender: Annotated[Gender, typer.Option("--g")] = Gender.FEMALE,
    age: Annotated[int | None, typer.Option("--a")] = None,
    password_length: Annotated[int, typer.Option("--q", "-q")] = 24,
    output_format: Annotated[str, typer.Option("--f")] = "pretty",
) -> None:
    output_format = _normalize_output_format(output_format)
    request = GenerationRequest(
        **_request_from_options(
            country=country,
            gender=gender,
            age=age,
            password_length=password_length,
        )
    )
    profile = asyncio.run(generator.generate_profile(request))
    data = formatter.format_profile(profile, debug=False, legacy=False, include_cli_hints=True)
    _emit(data, output_format, debug=False)


@app.command("generate-batch")
def generate_batch(
    count: Annotated[int, typer.Option("--count")] = 10,
    country: Annotated[str, typer.Option("--c")] = settings.default_country_code,
    gender: Annotated[Gender, typer.Option("--g")] = Gender.FEMALE,
    age: Annotated[int | None, typer.Option("--a")] = None,
    password_length: Annotated[int, typer.Option("--q", "-q")] = 24,
    output_format: Annotated[str, typer.Option("--f")] = "pretty",
) -> None:
    output_format = _normalize_output_format(output_format)
    request = BatchGenerationRequest(
        count=count,
        **_request_from_options(
            country=country,
            gender=gender,
            age=age,
            password_length=password_length,
        ),
    )
    response = asyncio.run(generator.generate_batch(request))
    data = formatter.format_batch(response, debug=False, legacy=False, include_cli_hints=True)
    _emit(data, output_format, debug=False)


@app.command("countries")
def countries() -> None:
    typer.echo(json.dumps(registry.list_countries(), indent=2))


def main() -> None:
    app()

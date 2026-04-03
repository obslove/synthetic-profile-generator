from __future__ import annotations

import asyncio
import logging
from typing import Annotated

import typer
from pydantic import BaseModel, ValidationError

from synthetic_profiles.bootstrap import build_profile_generator
from synthetic_profiles.config.logging import configure_logging
from synthetic_profiles.config.settings import Settings
from synthetic_profiles.models.enums import Gender, ResponseMode
from synthetic_profiles.models.schemas import BatchGenerationRequest, GenerationRequest
from synthetic_profiles.services.country_registry import CountryRegistry
from synthetic_profiles.services.output_formatter import OutputFormatter
from synthetic_profiles.utils.exceptions import UnsupportedCountryError, UnsupportedSubdivisionError

configure_logging(level=logging.ERROR)
app = typer.Typer(
    help=(
        "CLI do gerador de perfis sintéticos. "
        "Para aliases reais via SimpleLogin, configure SIMPLELOGIN_API_KEY no .env. "
        "Sem isso, o projeto usa fallback em example.*."
    )
)
settings = Settings()
generator = build_profile_generator(settings)
registry = CountryRegistry()
formatter = OutputFormatter()

def _normalize_output_format(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in {"compact", "pretty"}:
        raise typer.BadParameter("o formato deve ser um destes: compact, pretty")
    return normalized


def _emit(data: object, output_format: str) -> None:
    if output_format == "compact":
        typer.echo(formatter.to_compact_text(data, debug=False))
        return
    typer.echo(formatter.to_pretty_text(data, debug=False))


def _build_request(model_type: type[BaseModel], payload: dict[str, object]) -> BaseModel:
    try:
        return model_type(**payload)
    except ValidationError as exc:
        messages = [error["msg"] for error in exc.errors()]
        raise typer.BadParameter("; ".join(messages)) from exc


def _request_from_options(
    *,
    country: str,
    state: str | None,
    city: str | None,
    gender: Gender,
    age: int | None,
    use_simplelogin: bool,
) -> dict[str, object]:
    age_min = age if age is not None else 16
    age_max = age if age is not None else 78
    return {
        "country_code": country,
        "state": state,
        "city": city,
        "gender": gender,
        "age_min": age_min,
        "age_max": age_max,
        "password_length": 24,
        "use_simplelogin": use_simplelogin,
        "include_national_identifier": True,
        "seed": None,
        "debug_output": False,
        "response_mode": ResponseMode.CLEAN,
    }


@app.command("generate")
def generate(
    country: Annotated[str, typer.Option("--c")] = settings.default_country_code,
    state: Annotated[str | None, typer.Option("--s")] = None,
    city: Annotated[str | None, typer.Option("--ci")] = None,
    gender: Annotated[Gender, typer.Option("--g")] = Gender.FEMALE,
    age: Annotated[int | None, typer.Option("--a")] = None,
    use_simplelogin: Annotated[
        bool,
        typer.Option(
            "--sl/--no-sl",
            help=(
                "Usa SimpleLogin para aliases reais. "
                "Requer SIMPLELOGIN_API_KEY no .env; sem isso cai em fallback example.*."
            ),
        ),
    ] = True,
    output_format: Annotated[
        str,
        typer.Option("--f", help="Formato de saída: pretty ou compact."),
    ] = "pretty",
) -> None:
    output_format = _normalize_output_format(output_format)
    request = _build_request(
        GenerationRequest,
        _request_from_options(
            country=country,
            state=state,
            city=city,
            gender=gender,
            age=age,
            use_simplelogin=use_simplelogin,
        ),
    )
    profile = asyncio.run(generator.generate_profile(request))
    data = formatter.format_profile(
        profile,
        debug=False,
        legacy=False,
        include_cli_hints=True,
    )
    _emit(data, output_format)


@app.command("generate-batch")
def generate_batch(
    count: Annotated[int, typer.Option("--n", help="Quantidade de perfis.")] = 10,
    country: Annotated[str, typer.Option("--c")] = settings.default_country_code,
    state: Annotated[str | None, typer.Option("--s")] = None,
    city: Annotated[str | None, typer.Option("--ci")] = None,
    gender: Annotated[Gender, typer.Option("--g")] = Gender.FEMALE,
    age: Annotated[int | None, typer.Option("--a")] = None,
    use_simplelogin: Annotated[
        bool,
        typer.Option(
            "--sl/--no-sl",
            help=(
                "Usa SimpleLogin para aliases reais. "
                "Requer SIMPLELOGIN_API_KEY no .env; sem isso cai em fallback example.*."
            ),
        ),
    ] = True,
    output_format: Annotated[
        str,
        typer.Option("--f", help="Formato de saída: pretty ou compact."),
    ] = "pretty",
) -> None:
    output_format = _normalize_output_format(output_format)
    request = _build_request(
        BatchGenerationRequest,
        {
            "count": count,
            **_request_from_options(
                country=country,
                state=state,
                city=city,
                gender=gender,
                age=age,
                use_simplelogin=use_simplelogin,
            ),
        },
    )
    response = asyncio.run(generator.generate_batch(request))
    data = formatter.format_batch(
        response,
        debug=False,
        legacy=False,
        include_cli_hints=True,
    )
    _emit(data, output_format)


@app.command("countries")
def countries(
    output_format: Annotated[str, typer.Option("--f")] = "pretty",
) -> None:
    output_format = _normalize_output_format(output_format)
    data = formatter.format_countries(registry.list_countries())
    _emit(data, output_format)


@app.command("states")
def states(
    country: Annotated[str, typer.Option("--c")] = settings.default_country_code,
    output_format: Annotated[str, typer.Option("--f")] = "pretty",
) -> None:
    output_format = _normalize_output_format(output_format)
    try:
        normalized_country = country.strip().upper()
        pack, _ = registry.get_pack(normalized_country)
        subdivisions = registry.list_subdivisions(normalized_country)
    except UnsupportedCountryError as exc:
        raise typer.BadParameter(str(exc)) from exc
    data = formatter.format_subdivisions(
        subdivisions,
        country_code=pack.country_code,
        country_name=pack.country_name,
    )
    _emit(data, output_format)


@app.command("cities")
def cities(
    country: Annotated[str, typer.Option("--c")] = settings.default_country_code,
    state: Annotated[str, typer.Option("--s")] = ...,
    output_format: Annotated[str, typer.Option("--f")] = "pretty",
) -> None:
    output_format = _normalize_output_format(output_format)
    try:
        normalized_country = country.strip().upper()
        pack, _ = registry.get_pack(normalized_country)
        cities_data = registry.list_cities(normalized_country, state)
    except (UnsupportedCountryError, UnsupportedSubdivisionError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    if cities_data:
        subdivision_name = str(cities_data[0]["subdivision_name"])
        subdivision_code = str(cities_data[0]["subdivision_code"])
        subdivision_type = str(cities_data[0]["subdivision_type"])
    else:
        subdivision_name = state
        subdivision_code = state
        subdivision_type = "subdivisão"
    data = formatter.format_cities(
        cities_data,
        country_code=pack.country_code,
        country_name=pack.country_name,
        subdivision_code=subdivision_code,
        subdivision_name=subdivision_name,
        subdivision_type=subdivision_type,
    )
    _emit(data, output_format)


def main() -> None:
    app()

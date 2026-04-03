from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True, slots=True)
class CityEntry:
    name: str
    aliases: tuple[str, ...] = ()
    is_capital: bool = False


CATALOG_PATH = Path(__file__).with_name("city_catalog.json")


@lru_cache(maxsize=1)
def _load_catalog() -> dict[tuple[str, str], tuple[CityEntry, ...]]:
    raw_catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    catalog: dict[tuple[str, str], tuple[CityEntry, ...]] = {}
    for country_code, subdivision_map in raw_catalog.items():
        for subdivision_code, city_items in subdivision_map.items():
            catalog[(country_code, subdivision_code)] = tuple(
                CityEntry(
                    name=item["name"],
                    aliases=tuple(item.get("aliases", [])),
                    is_capital=bool(item.get("is_capital", False)),
                )
                for item in city_items
            )
    return catalog


def list_cities(country_code: str, subdivision_code: str) -> tuple[CityEntry, ...]:
    return _load_catalog().get((country_code, subdivision_code), ())


def resolve_city(
    country_code: str,
    subdivision_code: str,
    city_query: str | None,
) -> CityEntry | None:
    if city_query is None:
        return None
    normalized_query = _normalize_text(city_query)
    if not normalized_query:
        return None

    cities = list_cities(country_code, subdivision_code)

    exact_matches = [
        city
        for city in cities
        if normalized_query == _normalize_text(city.name)
        or normalized_query in {_normalize_text(alias) for alias in city.aliases}
    ]
    if exact_matches:
        return exact_matches[0]

    if len(normalized_query) >= 3:
        partial_matches = [
            city
            for city in cities
            if normalized_query in _normalize_text(city.name)
            or any(normalized_query in _normalize_text(alias) for alias in city.aliases)
        ]
        if partial_matches:
            return partial_matches[0]

    return None


def city_choices(country_code: str, subdivision_code: str, *, limit: int = 15) -> str:
    cities = list_cities(country_code, subdivision_code)
    visible = cities[:limit]
    rendered = ", ".join(city.name for city in visible)
    hidden_count = len(cities) - len(visible)
    if hidden_count <= 0:
        return rendered
    return f"{rendered}, ... e mais {hidden_count}"


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip())
    without_accents = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    sanitized = "".join(
        char if char.isalnum() else " "
        for char in without_accents.casefold()
    )
    return " ".join(sanitized.split())

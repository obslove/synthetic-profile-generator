from __future__ import annotations

import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CountrySubdivision:
    code: str
    name: str
    subdivision_type: str
    aliases: tuple[str, ...] = ()


TYPE_PRIORITY = {
    "state": 10,
    "district": 20,
    "territory": 30,
    "region": 40,
    "department": 50,
    "collectivity": 60,
}


SUBDIVISIONS_BY_COUNTRY: dict[str, tuple[CountrySubdivision, ...]] = {
    "BR": (
        CountrySubdivision("AC", "Acre", "state"),
        CountrySubdivision("AL", "Alagoas", "state"),
        CountrySubdivision("AP", "Amapá", "state"),
        CountrySubdivision("AM", "Amazonas", "state"),
        CountrySubdivision("BA", "Bahia", "state"),
        CountrySubdivision("CE", "Ceará", "state"),
        CountrySubdivision("DF", "Distrito Federal", "state"),
        CountrySubdivision("ES", "Espírito Santo", "state"),
        CountrySubdivision("GO", "Goiás", "state"),
        CountrySubdivision("MA", "Maranhão", "state"),
        CountrySubdivision("MT", "Mato Grosso", "state"),
        CountrySubdivision("MS", "Mato Grosso do Sul", "state"),
        CountrySubdivision("MG", "Minas Gerais", "state"),
        CountrySubdivision("PA", "Pará", "state"),
        CountrySubdivision("PB", "Paraíba", "state"),
        CountrySubdivision("PR", "Paraná", "state"),
        CountrySubdivision("PE", "Pernambuco", "state"),
        CountrySubdivision("PI", "Piauí", "state"),
        CountrySubdivision("RJ", "Rio de Janeiro", "state"),
        CountrySubdivision("RN", "Rio Grande do Norte", "state"),
        CountrySubdivision("RS", "Rio Grande do Sul", "state"),
        CountrySubdivision("RO", "Rondônia", "state"),
        CountrySubdivision("RR", "Roraima", "state"),
        CountrySubdivision("SC", "Santa Catarina", "state"),
        CountrySubdivision("SP", "São Paulo", "state"),
        CountrySubdivision("SE", "Sergipe", "state"),
        CountrySubdivision("TO", "Tocantins", "state"),
    ),
    "US": (
        CountrySubdivision("AL", "Alabama", "state"),
        CountrySubdivision("AK", "Alaska", "state"),
        CountrySubdivision("AZ", "Arizona", "state"),
        CountrySubdivision("AR", "Arkansas", "state"),
        CountrySubdivision("CA", "California", "state"),
        CountrySubdivision("CO", "Colorado", "state"),
        CountrySubdivision("CT", "Connecticut", "state"),
        CountrySubdivision("DE", "Delaware", "state"),
        CountrySubdivision("FL", "Florida", "state"),
        CountrySubdivision("GA", "Georgia", "state"),
        CountrySubdivision("HI", "Hawaii", "state"),
        CountrySubdivision("ID", "Idaho", "state"),
        CountrySubdivision("IL", "Illinois", "state"),
        CountrySubdivision("IN", "Indiana", "state"),
        CountrySubdivision("IA", "Iowa", "state"),
        CountrySubdivision("KS", "Kansas", "state"),
        CountrySubdivision("KY", "Kentucky", "state"),
        CountrySubdivision("LA", "Louisiana", "state"),
        CountrySubdivision("ME", "Maine", "state"),
        CountrySubdivision("MD", "Maryland", "state"),
        CountrySubdivision("MA", "Massachusetts", "state"),
        CountrySubdivision("MI", "Michigan", "state"),
        CountrySubdivision("MN", "Minnesota", "state"),
        CountrySubdivision("MS", "Mississippi", "state"),
        CountrySubdivision("MO", "Missouri", "state"),
        CountrySubdivision("MT", "Montana", "state"),
        CountrySubdivision("NE", "Nebraska", "state"),
        CountrySubdivision("NV", "Nevada", "state"),
        CountrySubdivision("NH", "New Hampshire", "state"),
        CountrySubdivision("NJ", "New Jersey", "state"),
        CountrySubdivision("NM", "New Mexico", "state"),
        CountrySubdivision("NY", "New York", "state"),
        CountrySubdivision("NC", "North Carolina", "state"),
        CountrySubdivision("ND", "North Dakota", "state"),
        CountrySubdivision("OH", "Ohio", "state"),
        CountrySubdivision("OK", "Oklahoma", "state"),
        CountrySubdivision("OR", "Oregon", "state"),
        CountrySubdivision("PA", "Pennsylvania", "state"),
        CountrySubdivision("RI", "Rhode Island", "state"),
        CountrySubdivision("SC", "South Carolina", "state"),
        CountrySubdivision("SD", "South Dakota", "state"),
        CountrySubdivision("TN", "Tennessee", "state"),
        CountrySubdivision("TX", "Texas", "state"),
        CountrySubdivision("UT", "Utah", "state"),
        CountrySubdivision("VT", "Vermont", "state"),
        CountrySubdivision("VA", "Virginia", "state"),
        CountrySubdivision("WA", "Washington", "state"),
        CountrySubdivision("WV", "West Virginia", "state"),
        CountrySubdivision("WI", "Wisconsin", "state"),
        CountrySubdivision("WY", "Wyoming", "state"),
        CountrySubdivision("DC", "District of Columbia", "district"),
        CountrySubdivision("AS", "American Samoa", "territory"),
        CountrySubdivision("GU", "Guam", "territory"),
        CountrySubdivision("MP", "Northern Mariana Islands", "territory"),
        CountrySubdivision("PR", "Puerto Rico", "territory"),
        CountrySubdivision("VI", "U.S. Virgin Islands", "territory", aliases=("US Virgin Islands",)),
    ),
}


def list_subdivisions(country_code: str) -> tuple[CountrySubdivision, ...]:
    return SUBDIVISIONS_BY_COUNTRY.get(country_code, ())


def subdivision_type_for(country_code: str) -> str | None:
    subdivision_types = subdivision_types_for(country_code)
    if not subdivision_types:
        return None
    if len(subdivision_types) == 1:
        return subdivision_types[0]
    return "mixed"


def subdivision_types_for(country_code: str) -> tuple[str, ...]:
    seen: dict[str, None] = {}
    for subdivision in list_subdivisions(country_code):
        seen.setdefault(subdivision.subdivision_type, None)
    return tuple(seen.keys())


def resolve_subdivision(
    country_code: str,
    subdivision_query: str | None,
) -> CountrySubdivision | None:
    if subdivision_query is None:
        return None
    normalized_query = _normalize_text(subdivision_query)
    if not normalized_query:
        return None

    exact_code_matches = [
        subdivision
        for subdivision in list_subdivisions(country_code)
        if normalized_query == _normalize_text(subdivision.code)
        or normalized_query in {_normalize_text(alias) for alias in subdivision.aliases}
    ]
    if exact_code_matches:
        return _best_match(exact_code_matches)

    exact_name_matches = [
        subdivision
        for subdivision in list_subdivisions(country_code)
        if normalized_query == _normalize_text(subdivision.name)
        or normalized_query in {_normalize_text(alias) for alias in subdivision.aliases}
    ]
    if exact_name_matches:
        return _best_match(exact_name_matches)

    if len(normalized_query) >= 3:
        contains_name_matches = [
            subdivision
            for subdivision in list_subdivisions(country_code)
            if normalized_query in _normalize_text(subdivision.name)
            or any(normalized_query in _normalize_text(alias) for alias in subdivision.aliases)
        ]
        if contains_name_matches:
            return _best_match(contains_name_matches)

    return None


def subdivision_choices(country_code: str, *, limit: int = 20) -> str:
    subdivisions = list_subdivisions(country_code)
    visible = subdivisions[:limit]
    rendered = ", ".join(
        f"{subdivision.code} ({subdivision.name})" for subdivision in visible
    )
    hidden_count = len(subdivisions) - len(visible)
    if hidden_count <= 0:
        return rendered
    return f"{rendered}, ... e mais {hidden_count}"


def _best_match(matches: list[CountrySubdivision]) -> CountrySubdivision:
    return sorted(
        matches,
        key=lambda subdivision: (
            TYPE_PRIORITY.get(subdivision.subdivision_type, 999),
            subdivision.code,
        ),
    )[0]


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip())
    without_accents = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return " ".join(without_accents.casefold().split())

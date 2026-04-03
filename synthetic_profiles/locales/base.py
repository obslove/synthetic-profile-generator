from __future__ import annotations

from dataclasses import dataclass

from synthetic_profiles.locales.countries.subdivisions import CountrySubdivision


@dataclass(frozen=True, slots=True)
class CountryPack:
    country_code: str
    country_name: str
    languages: tuple[str, ...]
    naming_style: str
    subdivision_type: str | None
    subdivision_types: tuple[str, ...]
    subdivisions: tuple[CountrySubdivision, ...]
    male_first_names: tuple[str, ...]
    female_first_names: tuple[str, ...]
    surnames: tuple[str, ...]

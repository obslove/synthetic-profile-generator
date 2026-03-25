from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CountryPack:
    country_code: str
    country_name: str
    languages: tuple[str, ...]
    naming_style: str
    male_first_names: tuple[str, ...]
    female_first_names: tuple[str, ...]
    surnames: tuple[str, ...]

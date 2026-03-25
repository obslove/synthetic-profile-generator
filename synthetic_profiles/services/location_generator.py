from __future__ import annotations

from synthetic_profiles.locales.base import CountryPack
from synthetic_profiles.models.schemas import Location


class LocationGenerator:
    """Return only the country-level location requested by the simplified generator."""

    def generate(self, *, pack: CountryPack) -> Location:
        return Location(country=pack.country_name, country_code=pack.country_code)

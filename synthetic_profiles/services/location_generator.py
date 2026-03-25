from __future__ import annotations

from synthetic_profiles.locales.base import CountryPack
from synthetic_profiles.models.schemas import Location


class LocationGenerator:
    """Retorna apenas a localização em nível de país do gerador simplificado."""

    def generate(self, *, pack: CountryPack) -> Location:
        return Location(country=pack.country_name, country_code=pack.country_code)

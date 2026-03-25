from __future__ import annotations

from synthetic_profiles.locales.base import CountryPack
from synthetic_profiles.models.schemas import CountryPackMetadata
from synthetic_profiles.services.country_registry import CountryRegistry


class LocaleResolver:
    """Resolve a country code to the best available locale pack."""

    def __init__(self, registry: CountryRegistry) -> None:
        self._registry = registry

    def resolve(self, country_code: str) -> tuple[CountryPack, CountryPackMetadata]:
        return self._registry.get_pack(country_code)

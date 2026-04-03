from __future__ import annotations

from synthetic_profiles.locales.base import CountryPack
from synthetic_profiles.locales.countries.cities import list_cities
from synthetic_profiles.locales.countries.starter_packs import STARTER_PACKS
from synthetic_profiles.locales.countries.subdivisions import resolve_subdivision
from synthetic_profiles.models.schemas import CountryPackMetadata
from synthetic_profiles.utils.exceptions import UnsupportedCountryError, UnsupportedSubdivisionError


class CountryRegistry:
    """Resolve metadados de país e pacotes de locale."""

    def __init__(self) -> None:
        self._starter_packs = STARTER_PACKS

    def is_valid_country_code(self, country_code: str) -> bool:
        return country_code in self._starter_packs

    def get_pack(self, country_code: str) -> tuple[CountryPack, CountryPackMetadata]:
        if not self.is_valid_country_code(country_code):
            raise UnsupportedCountryError(
                f"country_code não suportado: {country_code}. Os valores aceitos são BR e US."
            )
        pack = self._starter_packs[country_code]
        return pack, self._build_metadata(pack, fallback_used=False)

    def list_countries(self) -> list[dict[str, str | bool | int | list[str] | None]]:
        return [
            {
                "country_code": code,
                "country_name": pack.country_name,
                "has_bundled_pack": True,
                "subdivision_type": pack.subdivision_type,
                "subdivision_types": list(pack.subdivision_types),
                "subdivision_count": len(pack.subdivisions),
            }
            for code, pack in sorted(self._starter_packs.items())
        ]

    def list_subdivisions(self, country_code: str) -> list[dict[str, str]]:
        pack, _ = self.get_pack(country_code)
        return [
            {
                "code": subdivision.code,
                "name": subdivision.name,
                "type": subdivision.subdivision_type,
            }
            for subdivision in pack.subdivisions
        ]

    def list_cities(self, country_code: str, subdivision_query: str) -> list[dict[str, str | bool]]:
        pack, _ = self.get_pack(country_code)
        subdivision = resolve_subdivision(country_code, subdivision_query)
        if subdivision is None:
            raise UnsupportedSubdivisionError(
                f"subdivisão não suportada para {country_code}: {subdivision_query}"
            )
        return [
            {
                "name": city.name,
                "is_capital": city.is_capital,
                "subdivision_code": subdivision.code,
                "subdivision_name": subdivision.name,
                "subdivision_type": subdivision.subdivision_type,
            }
            for city in list_cities(pack.country_code, subdivision.code)
        ]

    def is_valid_subdivision(self, country_code: str, subdivision_query: str) -> bool:
        return resolve_subdivision(country_code, subdivision_query) is not None

    def _build_metadata(
        self,
        pack: CountryPack,
        *,
        fallback_used: bool,
        warnings: list[str] | None = None,
    ) -> CountryPackMetadata:
        return CountryPackMetadata(
            country_code=pack.country_code,
            country_name=pack.country_name,
            languages=list(pack.languages),
            naming_style=pack.naming_style,
            subdivision_type=pack.subdivision_type,
            subdivision_types=list(pack.subdivision_types),
            subdivision_count=len(pack.subdivisions),
            fallback_used=fallback_used,
            warnings=warnings or [],
        )

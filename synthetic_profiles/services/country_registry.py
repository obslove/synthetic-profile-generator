from __future__ import annotations

from synthetic_profiles.locales.base import CountryPack
from synthetic_profiles.locales.countries.starter_packs import STARTER_PACKS
from synthetic_profiles.models.schemas import CountryPackMetadata
from synthetic_profiles.utils.exceptions import UnsupportedCountryError


class CountryRegistry:
    """Resolve metadados de país e pacotes de locale."""

    def __init__(self) -> None:
        self._starter_packs = STARTER_PACKS

    def is_valid_country_code(self, country_code: str) -> bool:
        return country_code in self._starter_packs

    def get_pack(self, country_code: str) -> tuple[CountryPack, CountryPackMetadata]:
        if not self.is_valid_country_code(country_code):
            raise UnsupportedCountryError(
                f"country_code não suportado: {country_code}. Os valores aceitos são BR, US e FR."
            )
        pack = self._starter_packs[country_code]
        return pack, self._build_metadata(pack, fallback_used=False)

    def list_countries(self) -> list[dict[str, str | bool]]:
        return [
            {
                "country_code": code,
                "country_name": pack.country_name,
                "has_bundled_pack": True,
            }
            for code, pack in sorted(self._starter_packs.items())
        ]

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
            fallback_used=fallback_used,
            warnings=warnings or [],
        )

from __future__ import annotations

from synthetic_profiles.locales.base import CountryPack
from synthetic_profiles.locales.countries.cities import resolve_city
from synthetic_profiles.locales.countries.subdivisions import resolve_subdivision
from synthetic_profiles.models.schemas import Location


class LocationGenerator:
    """Resolve a localização em nível de país e, opcionalmente, subdivisão."""

    def generate(
        self,
        *,
        pack: CountryPack,
        state_query: str | None = None,
        city_query: str | None = None,
    ) -> Location:
        subdivision = resolve_subdivision(pack.country_code, state_query)
        city = (
            resolve_city(pack.country_code, subdivision.code, city_query)
            if subdivision is not None
            else None
        )
        return Location(
            country=pack.country_name,
            country_code=pack.country_code,
            state=subdivision.name if subdivision else None,
            state_code=subdivision.code if subdivision else None,
            state_type=subdivision.subdivision_type if subdivision else None,
            city=city.name if city else None,
        )

from __future__ import annotations

from synthetic_profiles.locales.base import CountryPack
from synthetic_profiles.locales.countries.name_pools import names_for


def pack(
    *,
    country_code: str,
    country_name: str,
    languages: tuple[str, ...],
    naming_style: str,
) -> CountryPack:
    return CountryPack(
        country_code=country_code,
        country_name=country_name,
        languages=languages,
        naming_style=naming_style,
        male_first_names=names_for(country_code, "male"),
        female_first_names=names_for(country_code, "female"),
        surnames=names_for(country_code, "surnames"),
    )


STARTER_PACKS: dict[str, CountryPack] = {
    "BR": pack(
        country_code="BR",
        country_name="Brasil",
        languages=("pt-BR",),
        naming_style="lusophone multi-surname",
    ),
    "US": pack(
        country_code="US",
        country_name="Estados Unidos",
        languages=("en-US",),
        naming_style="anglophone single-surname",
    ),
    "FR": pack(
        country_code="FR",
        country_name="França",
        languages=("fr-FR",),
        naming_style="francophone single-surname",
    ),
}

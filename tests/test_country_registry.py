from synthetic_profiles.services.country_registry import CountryRegistry
from synthetic_profiles.utils.exceptions import UnsupportedCountryError


def test_country_registry_returns_bundled_pack() -> None:
    registry = CountryRegistry()

    pack, metadata = registry.get_pack("BR")

    assert pack.country_code == "BR"
    assert metadata.fallback_used is False
    assert metadata.country_name == "Brazil"


def test_country_registry_lists_only_supported_countries() -> None:
    registry = CountryRegistry()

    countries = registry.list_countries()

    assert [item["country_code"] for item in countries] == ["BR", "FR", "US"]


def test_country_registry_rejects_invalid_code() -> None:
    registry = CountryRegistry()

    try:
        registry.get_pack("ZA")
    except UnsupportedCountryError:
        assert True
    else:
        assert False, "Expected UnsupportedCountryError"

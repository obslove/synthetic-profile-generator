from synthetic_profiles.services.country_registry import CountryRegistry
from synthetic_profiles.utils.exceptions import UnsupportedCountryError


def test_country_registry_returns_bundled_pack() -> None:
    registry = CountryRegistry()

    pack, metadata = registry.get_pack("BR")

    assert pack.country_code == "BR"
    assert metadata.fallback_used is False
    assert metadata.country_name == "Brasil"


def test_country_registry_lists_only_supported_countries() -> None:
    registry = CountryRegistry()

    countries = registry.list_countries()

    assert [item["country_code"] for item in countries] == ["BR", "US"]
    assert all(item["subdivision_count"] > 0 for item in countries)
    us_entry = next(item for item in countries if item["country_code"] == "US")
    assert us_entry["subdivision_type"] == "mixed"
    assert us_entry["subdivision_types"] == ["state", "district", "territory"]


def test_country_registry_lists_subdivisions_for_country() -> None:
    registry = CountryRegistry()

    subdivisions = registry.list_subdivisions("BR")

    assert any(item["code"] == "SP" and item["name"] == "São Paulo" for item in subdivisions)


def test_country_registry_lists_expanded_us_subdivisions() -> None:
    registry = CountryRegistry()

    us_subdivisions = registry.list_subdivisions("US")

    assert len(us_subdivisions) == 56
    assert any(item["code"] == "DC" and item["type"] == "district" for item in us_subdivisions)
    assert any(item["code"] == "PR" and item["type"] == "territory" for item in us_subdivisions)


def test_country_registry_lists_cities_for_subdivision() -> None:
    registry = CountryRegistry()

    cities = registry.list_cities("BR", "SP")

    assert any(item["name"] == "São Paulo" and item["is_capital"] is True for item in cities)
    assert any(item["name"] == "Campinas" and item["is_capital"] is False for item in cities)


def test_country_registry_has_cities_for_every_supported_subdivision() -> None:
    registry = CountryRegistry()

    for country_code in ["BR", "US"]:
        subdivisions = registry.list_subdivisions(country_code)
        assert subdivisions
        for subdivision in subdivisions:
            cities = registry.list_cities(country_code, str(subdivision["code"]))
            assert cities, f"missing cities for {country_code}/{subdivision['code']}"


def test_country_registry_lists_cities_for_us_territory() -> None:
    registry = CountryRegistry()

    guam = registry.list_cities("US", "GU")

    assert any(item["name"] == "Hagatna" and item["is_capital"] is True for item in guam)


def test_country_registry_rejects_invalid_code() -> None:
    registry = CountryRegistry()

    try:
        registry.get_pack("ZA")
    except UnsupportedCountryError:
        assert True
    else:
        assert False, "Expected UnsupportedCountryError"

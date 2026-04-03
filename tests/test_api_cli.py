import asyncio
import httpx
from typer.testing import CliRunner

from synthetic_profiles.api.app import app
from synthetic_profiles.cli.app import app as cli_app


def test_api_health_and_profile_generation() -> None:
    async def run() -> tuple[httpx.Response, httpx.Response]:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            health = await client.get("/health")
            response = await client.post(
                "/generate-profile",
                json={
                    "country_code": "BR",
                    "gender": "male",
                    "use_simplelogin": False,
                    "seed": 10,
                    "include_national_identifier": True,
                },
            )
        return health, response

    health, response = asyncio.run(run())

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert response.status_code == 200
    payload = response.json()
    assert set(payload.keys()) >= {"identity", "location", "family", "credentials"}
    assert payload["location"]["country_code"] == "BR"
    assert payload["credentials"]["email"] is not None
    assert payload["credentials"]["password"] is not None
    assert payload["identity"]["national_identifier"] is not None
    assert payload["identity"]["national_identifier_type"] == "cpf"
    assert payload["family"]["father"]["national_identifier"] is not None
    assert payload["family"]["mother"]["national_identifier"] is not None


def test_api_accepts_legacy_include_cpf_alias() -> None:
    async def run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post(
                "/generate-profile",
                json={
                    "country_code": "US",
                    "gender": "female",
                    "use_simplelogin": False,
                    "seed": 22,
                    "include_cpf": False,
                },
            )

    response = asyncio.run(run())

    assert response.status_code == 200
    payload = response.json()
    assert payload["identity"]["national_identifier"] is None
    assert payload["family"]["father"]["national_identifier"] is None
    assert payload["family"]["mother"]["national_identifier"] is None


def test_api_countries_endpoint_returns_registry_entries() -> None:
    async def run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.get("/countries")

    response = asyncio.run(run())

    assert response.status_code == 200
    assert any(item["country_code"] == "US" for item in response.json())


def test_api_states_endpoint_returns_subdivisions() -> None:
    async def run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.get("/countries/US/states")

    response = asyncio.run(run())

    assert response.status_code == 200
    assert any(item["code"] == "CA" and item["name"] == "California" for item in response.json())
    assert any(item["code"] == "DC" and item["type"] == "district" for item in response.json())


def test_api_cities_endpoint_returns_cities_for_subdivision() -> None:
    async def run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.get("/countries/BR/subdivisions/SP/cities")

    response = asyncio.run(run())

    assert response.status_code == 200
    assert any(item["name"] == "São Paulo" and item["is_capital"] is True for item in response.json())
    assert any(item["name"] == "Campinas" and item["is_capital"] is False for item in response.json())


def test_api_generate_profile_accepts_state_selection() -> None:
    async def run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post(
                "/generate-profile",
                json={
                    "country_code": "US",
                    "state": "CA",
                    "gender": "female",
                    "use_simplelogin": False,
                    "seed": 11,
                },
            )

    response = asyncio.run(run())

    assert response.status_code == 200
    payload = response.json()
    assert payload["location"]["state"] == "California"
    assert payload["location"]["state_code"] == "CA"
    assert payload["location"]["state_type"] == "state"


def test_api_generate_profile_accepts_city_selection() -> None:
    async def run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post(
                "/generate-profile",
                json={
                    "country_code": "BR",
                    "state": "SP",
                    "city": "Campinas",
                    "gender": "female",
                    "use_simplelogin": False,
                    "seed": 17,
                },
            )

    response = asyncio.run(run())

    assert response.status_code == 200
    payload = response.json()
    assert payload["location"]["state"] == "São Paulo"
    assert payload["location"]["city"] == "Campinas"


def test_api_generate_profile_accepts_expanded_us_subdivision() -> None:
    async def run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post(
                "/generate-profile",
                json={
                    "country_code": "US",
                    "state": "PR",
                    "gender": "female",
                    "use_simplelogin": False,
                    "seed": 12,
                },
            )

    us_response = asyncio.run(run())

    assert us_response.status_code == 200
    assert us_response.json()["location"]["state_type"] == "territory"
    assert us_response.json()["location"]["state"] == "Puerto Rico"


def test_cli_generate_defaults_to_pretty_output() -> None:
    runner = CliRunner()

    result = runner.invoke(
        cli_app,
        [
            "generate",
            "--c",
            "US",
            "--g",
            "female",
            "--no-sl",
        ],
    )

    assert result.exit_code == 0
    assert "Identidade" in result.stdout
    assert "E-mail:" in result.stdout
    assert "Senha:" in result.stdout
    assert "Estados Unidos (US)" in result.stdout
    assert "SSN-like:" in result.stdout


def test_cli_generate_accepts_city_selection() -> None:
    runner = CliRunner()

    result = runner.invoke(
        cli_app,
        ["generate", "--c", "BR", "--s", "SP", "--ci", "Campinas", "--no-sl"],
    )

    assert result.exit_code == 0
    assert "Cidade: Campinas" in result.stdout


def test_cli_generate_batch_outputs_pretty() -> None:
    runner = CliRunner()

    result = runner.invoke(
        cli_app,
        [
            "generate-batch",
            "--n",
            "2",
            "--c",
            "US",
            "--no-sl",
        ],
    )

    assert result.exit_code == 0
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len([line for line in lines if "Perfil " in line]) == 2


def test_cli_generate_compact_output_still_available() -> None:
    runner = CliRunner()

    result = runner.invoke(
        cli_app,
        ["generate", "--c", "US", "--f", "compact", "--no-sl"],
    )

    assert result.exit_code == 0
    assert "Identidade" not in result.stdout
    assert "E-mail:" in result.stdout
    assert "Senha:" in result.stdout


def test_cli_generate_with_simplelogin_toggle_still_works() -> None:
    runner = CliRunner()

    result = runner.invoke(
        cli_app,
        ["generate", "--c", "US", "--no-sl"],
    )

    assert result.exit_code == 0
    assert "Provedor de e-mail:" not in result.stdout


def test_cli_a_sets_exact_age() -> None:
    runner = CliRunner()

    result = runner.invoke(
        cli_app,
        ["generate", "--c", "US", "--a", "41", "--no-sl"],
    )

    assert result.exit_code == 0
    assert "Idade: 41" in result.stdout


def test_cli_removed_advanced_flags_are_rejected() -> None:
    runner = CliRunner()

    for args in (
        ["generate", "--seed", "77"],
        ["generate", "--debug"],
        ["generate", "--no-national-id"],
        ["generate", "-q", "32"],
        ["generate", "--state", "SP"],
        ["generate", "--simplelogin"],
        ["generate", "--no-simplelogin"],
        ["generate", "--city", "Campinas"],
        ["generate-batch", "--count", "2"],
    ):
        result = runner.invoke(cli_app, args)
        assert result.exit_code != 0
        assert "No such option" in result.output


def test_cli_rejects_unknown_output_format() -> None:
    runner = CliRunner()

    result = runner.invoke(cli_app, ["generate", "--f", "json"])

    assert result.exit_code != 0
    assert "o formato deve ser um destes" in result.output


def test_cli_generate_accepts_state_selection() -> None:
    runner = CliRunner()

    result = runner.invoke(
        cli_app,
        ["generate", "--c", "BR", "--s", "SP", "--no-sl"],
    )

    assert result.exit_code == 0
    assert "Estado: São Paulo (SP)" in result.stdout


def test_cli_states_lists_subdivisions() -> None:
    runner = CliRunner()

    result = runner.invoke(
        cli_app,
        ["states", "--c", "US"],
    )

    assert result.exit_code == 0
    assert "Subdivisões" in result.stdout
    assert "País: Estados Unidos (US)" in result.stdout
    assert "Estado: California (CA)" in result.stdout


def test_cli_cities_lists_cities() -> None:
    runner = CliRunner()

    result = runner.invoke(
        cli_app,
        ["cities", "--c", "BR", "--s", "SP"],
    )

    assert result.exit_code == 0
    assert "Cidades" in result.stdout
    assert "Estado: São Paulo (SP)" in result.stdout
    assert "Cidade: São Paulo | capital" in result.stdout
    assert "Cidade: Campinas" in result.stdout


def test_cli_cities_can_be_compact() -> None:
    runner = CliRunner()

    result = runner.invoke(
        cli_app,
        ["cities", "--c", "US", "--s", "CA", "--f", "compact"],
    )

    assert result.exit_code == 0
    assert "Sacramento | capital=True" in result.stdout
    assert "Los Angeles | capital=False" in result.stdout


def test_cli_states_lists_expanded_subdivisions() -> None:
    runner = CliRunner()

    us_result = runner.invoke(cli_app, ["states", "--c", "US"])

    assert us_result.exit_code == 0
    assert "Distrito: District of Columbia (DC)" in us_result.stdout
    assert "Território: Puerto Rico (PR)" in us_result.stdout


def test_cli_countries_is_pretty_by_default() -> None:
    runner = CliRunner()

    result = runner.invoke(cli_app, ["countries"])

    assert result.exit_code == 0
    assert "Países" in result.stdout
    assert "Brasil (BR)" in result.stdout
    assert "Estados Unidos (US)" in result.stdout


def test_cli_countries_can_be_compact() -> None:
    runner = CliRunner()

    result = runner.invoke(cli_app, ["countries", "--f", "compact"])

    assert result.exit_code == 0
    assert "BR | Brasil | 27 | state" in result.stdout
    assert "US | Estados Unidos | 56 | state, district, territory" in result.stdout

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
                json={"country_code": "BR", "gender": "male", "use_simplelogin": False, "seed": 10, "include_cpf": True},
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


def test_api_countries_endpoint_returns_registry_entries() -> None:
    async def run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.get("/countries")

    response = asyncio.run(run())

    assert response.status_code == 200
    assert any(item["country_code"] == "US" for item in response.json())


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
        ],
    )

    assert result.exit_code == 0
    assert "Identidade" in result.stdout
    assert "E-mail:" in result.stdout
    assert "Senha:" in result.stdout
    assert "Estados Unidos (US)" in result.stdout
    assert "SSN-like:" in result.stdout
    assert "Provedor de e-mail: fallback (missing_api_key)" in result.stdout


def test_cli_generate_batch_outputs_pretty() -> None:
    runner = CliRunner()

    result = runner.invoke(
        cli_app,
        [
            "generate-batch",
            "--count",
            "2",
            "--c",
            "FR",
        ],
    )

    assert result.exit_code == 0
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len([line for line in lines if "Perfil " in line]) == 2


def test_pretty_and_compact_modes_surface_credentials() -> None:
    runner = CliRunner()

    pretty = runner.invoke(
        cli_app,
        ["generate", "--c", "US", "--f", "pretty"],
    )
    compact = runner.invoke(
        cli_app,
        ["generate", "--c", "US", "--f", "compact"],
    )

    assert pretty.exit_code == 0
    assert "Credenciais" in pretty.stdout
    assert "E-mail:" in pretty.stdout
    assert "Senha:" in pretty.stdout
    assert "Provedor de e-mail: fallback (missing_api_key)" in pretty.stdout
    assert compact.exit_code == 0
    assert "E-mail:" in compact.stdout
    assert "Senha:" in compact.stdout
    assert "Provedor de e-mail: fallback (missing_api_key)" in compact.stdout


def test_cli_rejects_json_and_csv_formats() -> None:
    runner = CliRunner()

    json_result = runner.invoke(cli_app, ["generate", "--f", "json"])
    csv_result = runner.invoke(cli_app, ["generate", "--f", "csv"])

    assert json_result.exit_code != 0
    assert "o formato deve ser um destes" in json_result.output
    assert csv_result.exit_code != 0
    assert "o formato deve ser um destes" in csv_result.output

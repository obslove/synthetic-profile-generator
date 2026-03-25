import asyncio
import httpx
import random

from synthetic_profiles.identifiers.placeholders import build_identifier_generators
from synthetic_profiles.providers.fallback_email import FallbackEmailProvider
from synthetic_profiles.providers.simplelogin import SimpleLoginProvider
from synthetic_profiles.services.email_generation import EmailGenerationService
from synthetic_profiles.utils.randomizer import GenerationContext


class FakeResponse:
    def __init__(self, status_code: int, payload: dict[str, object], url: str = "https://example.test/api") -> None:
        self.status_code = status_code
        self._payload = payload
        self.url = url

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("POST", self.url)
            raise httpx.HTTPStatusError("error", request=request, response=httpx.Response(self.status_code, request=request, json=self._payload))

    def json(self) -> dict[str, object]:
        return self._payload


class SuccessfulAsyncClient:
    last_url: str | None = None

    def __init__(self, *args, **kwargs) -> None:
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):
        SuccessfulAsyncClient.last_url = args[0]
        return FakeResponse(201, {"email": "alias1@simplelogin.io"}, url=args[0])


class FailingAsyncClient(SuccessfulAsyncClient):
    async def post(self, *args, **kwargs):
        raise httpx.TimeoutException("timeout")


class HttpErrorAsyncClient(SuccessfulAsyncClient):
    async def post(self, *args, **kwargs):
        return FakeResponse(404, {"error": "not found"}, url=args[0])


def test_simplelogin_success_path(monkeypatch) -> None:
    monkeypatch.setattr(httpx, "AsyncClient", SuccessfulAsyncClient)
    provider = SimpleLoginProvider(api_key="token", base_url="https://example.test", timeout_seconds=2)

    emails, metadata = asyncio.run(
        provider.generate_addresses(
            local_part_seed="synthetic.user",
            count=2,
            context=GenerationContext.create(seed=5),
        )
    )

    assert len(emails) == 2
    assert emails[0].address == "alias1@simplelogin.io"
    assert metadata.provider_selected.value == "simplelogin"
    assert metadata.fallback_occurred is False
    assert metadata.provider_reason_code == "simplelogin_success"
    assert SuccessfulAsyncClient.last_url == "https://example.test/api/alias/random/new"


def test_simplelogin_failure_falls_back_with_reason(monkeypatch) -> None:
    monkeypatch.setattr(httpx, "AsyncClient", FailingAsyncClient)
    simplelogin = SimpleLoginProvider(api_key="token", base_url="https://example.test", timeout_seconds=2)
    fallback = FallbackEmailProvider(["example.com"])
    service = EmailGenerationService(simplelogin_provider=simplelogin, fallback_provider=fallback)

    emails, metadata = asyncio.run(
        service.generate_addresses(
            profile_name="Synthetic User",
            count=2,
            use_simplelogin=True,
            context=GenerationContext.create(seed=42),
        )
    )

    assert len(emails) == 2
    assert all(email.address.endswith("@example.com") for email in emails)
    assert metadata.fallback_occurred is True
    assert metadata.provider_reason_code == "timeout"


def test_simplelogin_http_status_error_is_classified(monkeypatch) -> None:
    monkeypatch.setattr(httpx, "AsyncClient", HttpErrorAsyncClient)
    simplelogin = SimpleLoginProvider(api_key="token", base_url="https://example.test", timeout_seconds=2)
    fallback = FallbackEmailProvider(["example.com"])
    service = EmailGenerationService(simplelogin_provider=simplelogin, fallback_provider=fallback)

    emails, metadata = asyncio.run(
        service.generate_addresses(
            profile_name="Synthetic User",
            count=1,
            use_simplelogin=True,
            context=GenerationContext.create(seed=42),
        )
    )

    assert len(emails) == 1
    assert metadata.fallback_occurred is True
    assert metadata.provider_reason_code == "http_404"


def test_fallback_email_diversity_changes_without_seed() -> None:
    provider = FallbackEmailProvider(["example.com"])
    first, _ = asyncio.run(
        provider.generate_addresses(
            local_part_seed="synthetic.user",
            count=3,
            context=GenerationContext.create(seed=None),
        )
    )
    second, _ = asyncio.run(
        provider.generate_addresses(
            local_part_seed="synthetic.user",
            count=3,
            context=GenerationContext.create(seed=None),
        )
    )

    assert [email.address for email in first] != [email.address for email in second]


def test_identifier_generation_is_test_only() -> None:
    generators = build_identifier_generators(strict_identifier_safety_mode=True)

    cpf = generators[("BR", "cpf")].generate(random.Random(1))
    ssn_like = generators[("US", "ssn_like")].generate(random.Random(2))
    nir_like = generators[("FR", "nir_like")].generate(random.Random(3))

    assert cpf.safe_for_testing_only is True
    assert cpf.is_synthetic_identifier is True
    assert cpf.formatted_value == "291.417.776-38"
    assert ssn_like.safe_for_testing_only is True
    assert ssn_like.identifier_type == "ssn_like"
    assert ssn_like.formatted_value.startswith("000-")
    assert nir_like.safe_for_testing_only is True
    assert nir_like.identifier_type == "nir_like"
    assert nir_like.formatted_value.startswith("7 ")

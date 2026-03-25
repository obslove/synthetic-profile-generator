from __future__ import annotations

import logging
from urllib.parse import urlparse

import httpx

from synthetic_profiles.models.enums import EmailProviderName
from synthetic_profiles.models.schemas import GeneratedEmail, ProviderMetadata
from synthetic_profiles.providers.base import EmailProvider
from synthetic_profiles.utils.exceptions import EmailProviderError
from synthetic_profiles.utils.randomizer import GenerationContext

LOGGER = logging.getLogger(__name__)


class SimpleLoginProvider(EmailProvider):
    """Provedor de aliases do SimpleLogin com tratamento de erro normalizado."""

    def __init__(self, *, api_key: str, base_url: str, timeout_seconds: float) -> None:
        self._api_key = api_key
        self._base_url = self._normalize_base_url(base_url)
        self._timeout_seconds = timeout_seconds

    async def generate_addresses(
        self,
        *,
        local_part_seed: str,
        count: int,
        context: GenerationContext,
    ) -> tuple[list[GeneratedEmail], ProviderMetadata]:
        headers = {"Authentication": self._api_key}
        generated_emails: list[GeneratedEmail] = []
        total_retries = 0
        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            for alias_index in range(count):
                retries = 0
                payload = {"note": f"synthetic-profile:{local_part_seed}:{alias_index + 1}"}
                while True:
                    try:
                        response = await client.post(
                            f"{self._base_url}/alias/random/new",
                            headers=headers,
                            json=payload,
                        )
                        if response.status_code in {401, 403}:
                            raise EmailProviderError("Falha de autenticação no SimpleLogin", reason_code="auth_failure")
                        if response.status_code == 429:
                            raise EmailProviderError("Limite de requisições do SimpleLogin atingido", reason_code="rate_limit")
                        response.raise_for_status()
                        data = response.json()
                        aliases = self._normalize_aliases(data)
                        if not aliases:
                            raise EmailProviderError("O SimpleLogin não retornou aliases", reason_code="invalid_response")
                        generated_emails.extend(
                            [
                                GeneratedEmail(
                                    address=alias,
                                    provider=EmailProviderName.SIMPLELOGIN,
                                    is_alias=True,
                                    metadata={"source": "simplelogin"},
                                )
                                for alias in aliases
                            ]
                        )
                        break
                    except httpx.TimeoutException as exc:
                        LOGGER.warning(
                            "simplelogin_request_failed",
                            extra={"event": "simplelogin_request_failed", "metadata": {"error": "timeout", "retries": retries}},
                        )
                        if retries >= 1:
                            raise EmailProviderError("Tempo limite excedido na requisição ao SimpleLogin", reason_code="timeout") from exc
                        retries += 1
                        total_retries += 1
                    except httpx.ConnectError as exc:
                        LOGGER.warning(
                            "simplelogin_request_failed",
                            extra={"event": "simplelogin_request_failed", "metadata": {"error": "connect_error", "retries": retries}},
                        )
                        if retries >= 1:
                            raise EmailProviderError("Falha de conexão com o SimpleLogin", reason_code="connect_error") from exc
                        retries += 1
                        total_retries += 1
                    except httpx.HTTPStatusError as exc:
                        reason_code, message = self._status_error(exc)
                        LOGGER.warning(
                            "simplelogin_request_failed",
                            extra={
                                "event": "simplelogin_request_failed",
                                "metadata": {"error": reason_code, "retries": retries},
                            },
                        )
                        if retries >= 1:
                            raise EmailProviderError(message, reason_code=reason_code) from exc
                        retries += 1
                        total_retries += 1
                    except httpx.HTTPError as exc:
                        LOGGER.warning(
                            "simplelogin_request_failed",
                            extra={"event": "simplelogin_request_failed", "metadata": {"error": "transport_error", "retries": retries}},
                        )
                        if retries >= 1:
                            raise EmailProviderError("Erro de transporte ao acessar o SimpleLogin", reason_code="transport_error") from exc
                        retries += 1
                        total_retries += 1
                    except EmailProviderError as exc:
                        LOGGER.warning(
                            "simplelogin_request_failed",
                            extra={
                                "event": "simplelogin_request_failed",
                                "metadata": {"error": exc.reason_code, "retries": retries},
                            },
                        )
                        if retries >= 1 or exc.reason_code in {"auth_failure", "rate_limit", "invalid_response"}:
                            raise
                        retries += 1
                        total_retries += 1
        return (
            generated_emails[:count],
            ProviderMetadata(
                provider_selected=EmailProviderName.SIMPLELOGIN,
                retries_attempted=total_retries,
                fallback_occurred=False,
                simplelogin_requested=True,
                provider_reason="Geração de alias no SimpleLogin concluída com sucesso.",
                provider_reason_code="simplelogin_success",
            ),
        )

    def _normalize_aliases(self, data: dict[str, object]) -> list[str]:
        if isinstance(data.get("aliases"), list):
            return [str(item) for item in data["aliases"] if item]
        email = data.get("email")
        if email:
            return [str(email)]
        alias = data.get("alias")
        if alias:
            return [str(alias)]
        return []

    def _normalize_base_url(self, base_url: str) -> str:
        cleaned = base_url.rstrip("/")
        parsed = urlparse(cleaned)
        if not parsed.path:
            return f"{cleaned}/api"
        return cleaned

    def _status_error(self, exc: httpx.HTTPStatusError) -> tuple[str, str]:
        response = exc.response
        status_code = response.status_code
        reason_code = f"http_{status_code}"
        message = f"O SimpleLogin retornou HTTP {status_code}"
        try:
            data = response.json()
        except Exception:
            data = None
        if isinstance(data, dict) and data.get("error"):
            message = f"O SimpleLogin retornou HTTP {status_code}: {data['error']}"
        return reason_code, message

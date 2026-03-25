from __future__ import annotations

from synthetic_profiles.models.schemas import GeneratedEmail, ProviderMetadata
from synthetic_profiles.providers.base import EmailProvider
from synthetic_profiles.providers.fallback_email import FallbackEmailProvider
from synthetic_profiles.utils.exceptions import EmailProviderError
from synthetic_profiles.utils.randomizer import GenerationContext


class EmailGenerationService:
    """Orquestra a geração principal de aliases de e-mail com diagnóstico claro e fallback seguro."""

    def __init__(
        self,
        *,
        simplelogin_provider: EmailProvider | None,
        fallback_provider: FallbackEmailProvider,
    ) -> None:
        self._simplelogin_provider = simplelogin_provider
        self._fallback_provider = fallback_provider

    async def generate_addresses(
        self,
        *,
        profile_name: str,
        count: int,
        use_simplelogin: bool,
        context: GenerationContext,
    ) -> tuple[list[GeneratedEmail], ProviderMetadata]:
        local_part_seed = profile_name.lower().replace(" ", ".")
        fallback_context = context.child("email-fallback")
        if not use_simplelogin:
            emails, metadata = await self._fallback_provider.generate_addresses(
                local_part_seed=local_part_seed,
                count=count,
                context=fallback_context,
            )
            metadata.provider_reason = "Provedor SimpleLogin desativado pela requisição."
            metadata.provider_reason_code = "provider_disabled"
            return emails, metadata
        if self._simplelogin_provider is None:
            emails, metadata = await self._fallback_provider.generate_addresses(
                local_part_seed=local_part_seed,
                count=count,
                context=fallback_context,
            )
            metadata.fallback_occurred = True
            metadata.degraded_mode = True
            metadata.warning_message = "SimpleLogin solicitado, mas a chave de API está ausente. Fallback com domínio reservado utilizado."
            metadata.simplelogin_requested = True
            metadata.provider_reason = "Chave de API do SimpleLogin ausente."
            metadata.provider_reason_code = "missing_api_key"
            return emails, metadata
        try:
            return await self._simplelogin_provider.generate_addresses(
                local_part_seed=local_part_seed,
                count=count,
                context=context.child("simplelogin"),
            )
        except EmailProviderError as exc:
            emails, metadata = await self._fallback_provider.generate_addresses(
                local_part_seed=local_part_seed,
                count=count,
                context=fallback_context,
            )
            metadata.fallback_occurred = True
            metadata.degraded_mode = True
            metadata.simplelogin_requested = True
            metadata.warning_message = f"SimpleLogin indisponível: {exc}. Fallback com domínio reservado utilizado."
            metadata.provider_reason = str(exc)
            metadata.provider_reason_code = exc.reason_code
            return emails, metadata

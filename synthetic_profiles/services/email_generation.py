from __future__ import annotations

from synthetic_profiles.models.schemas import GeneratedEmail, ProviderMetadata
from synthetic_profiles.providers.base import EmailProvider
from synthetic_profiles.providers.fallback_email import FallbackEmailProvider
from synthetic_profiles.utils.exceptions import EmailProviderError
from synthetic_profiles.utils.randomizer import GenerationContext


class EmailGenerationService:
    """Orchestrate primary email alias generation with explicit diagnostics and safe fallback."""

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
            metadata.provider_reason = "SimpleLogin provider disabled by request."
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
            metadata.warning_message = "SimpleLogin requested but API key is missing. Reserved-domain fallback used."
            metadata.simplelogin_requested = True
            metadata.provider_reason = "SimpleLogin API key missing."
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
            metadata.warning_message = f"SimpleLogin unavailable: {exc}. Reserved-domain fallback used."
            metadata.provider_reason = str(exc)
            metadata.provider_reason_code = exc.reason_code
            return emails, metadata

from __future__ import annotations

import re

from synthetic_profiles.models.enums import EmailProviderName
from synthetic_profiles.models.schemas import GeneratedEmail, ProviderMetadata
from synthetic_profiles.providers.base import EmailProvider
from synthetic_profiles.utils.randomizer import GenerationContext


class FallbackEmailProvider(EmailProvider):
    """Gera endereços claramente sintéticos em domínios reservados com estratégias variadas."""

    descriptor_words = (
        "lab",
        "demo",
        "seed",
        "sandbox",
        "atlas",
        "ember",
        "cobalt",
        "nova",
        "pixel",
        "cinder",
        "harbor",
        "signal",
        "vector",
        "mint",
        "glint",
        "orbit",
        "sprout",
        "quartz",
    )
    separators = (".", "_", "-", "")

    def __init__(self, domains: list[str]) -> None:
        self._domains = domains or ["example.com", "example.org", "example.net"]

    async def generate_addresses(
        self,
        *,
        local_part_seed: str,
        count: int,
        context: GenerationContext,
    ) -> tuple[list[GeneratedEmail], ProviderMetadata]:
        rng = context.rng("fallback-email", local_part_seed, count)
        parts = [part for part in re.split(r"[^a-z0-9]+", local_part_seed.lower()) if part]
        first = parts[0] if parts else "synthetic"
        last = parts[-1] if len(parts) > 1 else "profile"
        initials = "".join(part[0] for part in parts[:3]) or "sp"
        base_slug = re.sub(r"[^a-z0-9]+", ".", local_part_seed.lower()).strip(".") or "synthetic.user"
        strategies = [
            lambda: f"{first}{rng.choice(self.separators)}{last}",
            lambda: f"{initials}{rng.choice(self.separators)}{last}",
            lambda: f"{first}{rng.choice(self.separators)}{rng.choice(self.descriptor_words)}{rng.randint(11, 99)}",
            lambda: f"{rng.choice(self.descriptor_words)}{rng.choice(self.separators)}{last}{rng.randint(100, 999)}",
            lambda: f"{first}{rng.choice(self.separators)}{last}{rng.choice(self.separators)}qa",
            lambda: f"{base_slug.replace('.', rng.choice(self.separators))[:18]}{rng.randint(1984, 2029)}",
            lambda: f"{first[:1]}{last[:6]}{rng.choice(self.separators)}{rng.randint(10, 999)}",
            lambda: f"{rng.choice(self.descriptor_words)}{rng.choice(self.separators)}{first}{rng.choice(self.separators)}{rng.randint(10, 99)}",
            lambda: f"{first}{rng.choice(self.separators)}{last[:4]}{rng.choice(self.separators)}test",
            lambda: f"{initials}{rng.choice(self.separators)}{rng.choice(self.descriptor_words)}{rng.randint(1000, 9999)}",
        ]
        addresses: list[GeneratedEmail] = []
        seen: set[str] = set()
        while len(addresses) < count:
            local_part = rng.choice(strategies)().strip("._-") or "synthetic-user"
            address = f"{local_part}@{rng.choice(self._domains)}"
            if address in seen:
                continue
            seen.add(address)
            addresses.append(
                GeneratedEmail(
                    address=address,
                    provider=EmailProviderName.FALLBACK,
                    is_alias=False,
                    metadata={"format": "synthetic_reserved_domain"},
                )
            )
        return addresses, ProviderMetadata(
            provider_selected=EmailProviderName.FALLBACK,
            fallback_occurred=False,
            warning_message="Provedor de fallback com domínio reservado utilizado.",
            degraded_mode=False,
            provider_reason="Provedor de fallback selecionado para geração sintética em domínio reservado.",
            provider_reason_code="fallback_selected",
        )

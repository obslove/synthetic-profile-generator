from __future__ import annotations

from abc import ABC, abstractmethod

from synthetic_profiles.models.schemas import GeneratedEmail, ProviderMetadata
from synthetic_profiles.utils.randomizer import GenerationContext


class EmailProvider(ABC):
    """Email provider interface."""

    @abstractmethod
    async def generate_addresses(
        self,
        *,
        local_part_seed: str,
        count: int,
        context: GenerationContext,
    ) -> tuple[list[GeneratedEmail], ProviderMetadata]:
        raise NotImplementedError

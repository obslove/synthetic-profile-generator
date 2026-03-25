from __future__ import annotations

from abc import ABC, abstractmethod
import random

from synthetic_profiles.models.schemas import SyntheticIdentifier


class IdentifierGenerator(ABC):
    """Interface for test-only identifier generators."""

    country_code: str
    identifier_type: str

    @abstractmethod
    def generate(self, rng: random.Random) -> SyntheticIdentifier:
        raise NotImplementedError

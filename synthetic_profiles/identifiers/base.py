from __future__ import annotations

from abc import ABC, abstractmethod
import random

from synthetic_profiles.models.schemas import SyntheticIdentifier


class IdentifierGenerator(ABC):
    """Interface para geradores de identificadores apenas para teste."""

    country_code: str
    identifier_type: str

    @abstractmethod
    def generate(self, rng: random.Random) -> SyntheticIdentifier:
        raise NotImplementedError

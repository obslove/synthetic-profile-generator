from __future__ import annotations

import random

from synthetic_profiles.identifiers.base import IdentifierGenerator
from synthetic_profiles.models.schemas import SyntheticIdentifier


class BrazilCPFGenerator(IdentifierGenerator):
    country_code = "BR"
    identifier_type = "cpf"

    def __init__(self, *, allow_algorithmic_validity: bool = True) -> None:
        self._allow_algorithmic_validity = allow_algorithmic_validity

    def generate(self, rng: random.Random) -> SyntheticIdentifier:
        if not self._allow_algorithmic_validity:
            digits = [9, 9, rng.randint(0, 9), rng.randint(0, 9), rng.randint(0, 9), rng.randint(0, 9), rng.randint(0, 9), rng.randint(0, 9), 0, 0, 0]
        else:
            base = self._non_trivial_base(rng)
            base.extend(self._cpf_check_digits(base))
            digits = base
        raw = "".join(map(str, digits))
        formatted = f"{raw[:3]}.{raw[3:6]}.{raw[6:9]}-{raw[9:]}"
        return SyntheticIdentifier(
            value=raw,
            formatted_value=formatted,
            country_code=self.country_code,
            identifier_type=self.identifier_type,
        )

    def _non_trivial_base(self, rng: random.Random) -> list[int]:
        while True:
            digits = [rng.randint(0, 9) for _ in range(9)]
            if len(set(digits)) > 1:
                return digits

    def _cpf_check_digits(self, digits: list[int]) -> list[int]:
        first_total = sum(value * weight for value, weight in zip(digits, range(10, 1, -1), strict=True))
        first = (first_total * 10 % 11) % 10
        second_total = sum(value * weight for value, weight in zip(digits + [first], range(11, 1, -1), strict=True))
        second = (second_total * 10 % 11) % 10
        return [first, second]

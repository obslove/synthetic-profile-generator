from __future__ import annotations

import random

from synthetic_profiles.identifiers.base import IdentifierGenerator
from synthetic_profiles.models.schemas import SyntheticIdentifier


class PlaceholderIdentifierGenerator(IdentifierGenerator):
    def __init__(self, *, country_code: str, identifier_type: str, formatter) -> None:
        self.country_code = country_code
        self.identifier_type = identifier_type
        self._formatter = formatter

    def generate(self, rng: random.Random) -> SyntheticIdentifier:
        value, formatted = self._formatter(rng)
        return SyntheticIdentifier(
            value=value,
            formatted_value=formatted,
            country_code=self.country_code,
            identifier_type=self.identifier_type,
        )


def _us_ssn_like(rng: random.Random) -> tuple[str, str]:
    # Reserved-invalid 000 prefix keeps the value synthetic-only while staying UI-friendly.
    middle = rng.randint(10, 99)
    last = rng.randint(1000, 9999)
    raw = f"000{middle:02d}{last:04d}"
    formatted = f"000-{middle:02d}-{last:04d}"
    return raw, formatted


def _fr_nir_like(rng: random.Random) -> tuple[str, str]:
    # Leading 7 keeps the structure FR-like without creating a real-world compatible NIR.
    year = rng.randint(60, 99)
    month = rng.randint(1, 12)
    synthetic_department = 98
    commune = rng.randint(100, 999)
    order = rng.randint(100, 999)
    control = rng.randint(10, 97)
    raw = f"7{year:02d}{month:02d}{synthetic_department:02d}{commune:03d}{order:03d}{control:02d}"
    formatted = f"7 {year:02d} {month:02d} {synthetic_department:02d} {commune:03d} {order:03d} {control:02d}"
    return raw, formatted


def build_identifier_generators(*, strict_identifier_safety_mode: bool) -> dict[tuple[str, str], IdentifierGenerator]:
    return {
        ("BR", "cpf"): __import__(
            "synthetic_profiles.identifiers.brazil_cpf",
            fromlist=["BrazilCPFGenerator"],
        ).BrazilCPFGenerator(allow_algorithmic_validity=True),
        ("US", "ssn_like"): PlaceholderIdentifierGenerator(
            country_code="US",
            identifier_type="ssn_like",
            formatter=_us_ssn_like,
        ),
        ("FR", "nir_like"): PlaceholderIdentifierGenerator(
            country_code="FR",
            identifier_type="nir_like",
            formatter=_fr_nir_like,
        ),
    }

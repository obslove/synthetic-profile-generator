from __future__ import annotations

from synthetic_profiles.models.enums import Gender


class GenderResolver:
    """Retorna valores normalizados do enum de gênero."""

    def resolve(self, gender: Gender) -> Gender:
        return gender

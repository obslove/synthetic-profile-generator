from __future__ import annotations

from synthetic_profiles.models.enums import Gender


class GenderResolver:
    """Return normalized gender enum values."""

    def resolve(self, gender: Gender) -> Gender:
        return gender

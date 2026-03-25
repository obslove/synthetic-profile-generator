from __future__ import annotations

from enum import StrEnum


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"


class AgeGroup(StrEnum):
    CHILD = "child"
    TEENAGER = "teenager"
    ADULT = "adult"
    ELDERLY = "elderly"


class NameStructure(StrEnum):
    FIRST = "first_name"
    SHORT = "first_last"
    FULL = "full"


class Rarity(StrEnum):
    COMMON = "common"
    BALANCED = "balanced"
    UNCOMMON = "uncommon"


class ResponseMode(StrEnum):
    CLEAN = "clean"
    LEGACY = "legacy"


class EmailProviderName(StrEnum):
    SIMPLELOGIN = "simplelogin"
    FALLBACK = "fallback"

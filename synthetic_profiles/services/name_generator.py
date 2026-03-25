from __future__ import annotations

from synthetic_profiles.locales.base import CountryPack
from synthetic_profiles.models.enums import Gender, NameStructure, Rarity
from synthetic_profiles.utils.randomizer import GenerationContext, choice_with_penalty


class NameGenerator:
    """Generate locale-aware synthetic names with adaptive repetition penalties."""

    _blocked_full_names = {
        "lionel messi",
        "taylor swift",
        "michael jordan",
        "neymar santos",
        "cristiano ronaldo",
        "ana de armas",
    }

    def generate(
        self,
        context: GenerationContext,
        *,
        pack: CountryPack,
        gender: Gender,
        structure: NameStructure,
        rarity: Rarity,
    ) -> str:
        rng = context.rng("name")
        source = pack.male_first_names if gender is Gender.MALE else pack.female_first_names
        first = self._pick_name(rng, source, rarity, context, "first-name")
        middle_source = tuple(name for name in source if name != first) or source
        middle = self._pick_name(rng, middle_source, rarity, context, "middle-name")
        surnames = self._pick_surnames(rng, pack.surnames, pack.naming_style, rarity, context)
        if structure is NameStructure.FIRST:
            full_name = first
        elif structure is NameStructure.SHORT:
            full_name = f"{first} {surnames[0]}"
        else:
            parts = [first]
            if "double-surname" in pack.naming_style or "multi-surname" in pack.naming_style:
                parts.append(middle)
            parts.extend(surnames)
            full_name = " ".join(parts)
        if full_name.lower() in self._blocked_full_names:
            return self.generate(context.child("retry-name"), pack=pack, gender=gender, structure=structure, rarity=rarity)
        return full_name

    def _pick_name(
        self,
        rng,
        names: tuple[str, ...],
        rarity: Rarity,
        context: GenerationContext,
        key_prefix: str,
    ) -> str:
        pool = self._ordered_candidates(names, rarity)
        return choice_with_penalty(
            rng,
            pool,
            context.usage_counts,
            lambda item: f"{key_prefix}:{item}",
        )

    def _pick_surnames(
        self,
        rng,
        surnames: tuple[str, ...],
        naming_style: str,
        rarity: Rarity,
        context: GenerationContext,
    ) -> list[str]:
        pool = self._ordered_candidates(surnames, rarity)
        count = 2 if "double-surname" in naming_style or "multi-surname" in naming_style else 1
        if "mixed" in naming_style:
            count = rng.choice([1, 2])
        selected: list[str] = []
        available = list(pool)
        for index in range(count):
            value = choice_with_penalty(
                rng,
                available,
                context.usage_counts,
                lambda item: f"surname:{item}:{index}",
            )
            selected.append(value)
            available = [item for item in available if item != value]
        return selected

    def _ordered_candidates(self, values: tuple[str, ...], rarity: Rarity) -> tuple[str, ...]:
        if rarity is Rarity.COMMON:
            head = values[: min(80, len(values))]
            return (*head, *head, *head, *head)
        if rarity is Rarity.UNCOMMON:
            tail_start = min(len(values) // 2, 2500)
            tail = values[tail_start:]
            return (*tail, *tail[len(tail) // 3 :])
        head = values[: min(220, len(values))]
        upper_mid = values[: min(900, len(values))]
        return (*head, *head, *head, *upper_mid, *upper_mid)

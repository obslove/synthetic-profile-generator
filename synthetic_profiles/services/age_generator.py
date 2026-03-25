from __future__ import annotations

from synthetic_profiles.models.enums import AgeGroup
from synthetic_profiles.utils.randomizer import GenerationContext


class AgeGenerator:
    """Generate ages using a more natural weighted distribution."""

    def generate(self, context: GenerationContext, minimum: int, maximum: int) -> tuple[int, AgeGroup]:
        rng = context.rng("age")
        candidates = list(range(minimum, maximum + 1))
        weights = [self.age_weight(age) for age in candidates]
        age = rng.choices(candidates, weights=weights, k=1)[0]
        return age, self.group_for(age)

    def group_for(self, age: int) -> AgeGroup:
        if age < 13:
            return AgeGroup.CHILD
        if age < 18:
            return AgeGroup.TEENAGER
        if age < 65:
            return AgeGroup.ADULT
        return AgeGroup.ELDERLY

    def age_weight(self, age: int) -> float:
        if age < 13:
            return 0.35
        if age < 18:
            return 0.75
        if age < 25:
            return 1.55
        if age < 35:
            return 1.85
        if age < 45:
            return 1.45
        if age < 55:
            return 1.15
        if age < 65:
            return 0.95
        if age < 75:
            return 0.7
        return 0.5

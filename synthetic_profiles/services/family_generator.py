from __future__ import annotations

from synthetic_profiles.locales.base import CountryPack
from synthetic_profiles.models.enums import Gender, NameStructure, Rarity
from synthetic_profiles.models.schemas import Family, ParentIdentity, SyntheticIdentifier
from synthetic_profiles.services.name_generator import NameGenerator
from synthetic_profiles.utils.randomizer import GenerationContext


class FamilyGenerator:
    """Generate a minimal family structure with only synthetic parents."""

    def __init__(self, name_generator: NameGenerator) -> None:
        self._name_generator = name_generator

    def generate_parents(
        self,
        context: GenerationContext,
        *,
        pack: CountryPack,
        child_age: int,
        child_full_name: str,
        father_identifier: SyntheticIdentifier | None = None,
        mother_identifier: SyntheticIdentifier | None = None,
    ) -> Family:
        rng = context.rng("parents")
        father_surname, mother_surname = self._parent_surnames(pack=pack, child_full_name=child_full_name)
        father_age = max(child_age + rng.randint(22, 36), child_age + 20)
        mother_age = max(child_age + rng.randint(20, 34), child_age + 20)

        father_name = self._parent_name(
            context.child("father"),
            pack=pack,
            gender=Gender.MALE,
            surname_tail=father_surname,
        )
        mother_name = self._parent_name(
            context.child("mother"),
            pack=pack,
            gender=Gender.FEMALE,
            surname_tail=mother_surname,
            avoid_surname=father_surname,
        )
        return Family(
            father=ParentIdentity(
                full_name=father_name,
                gender=Gender.MALE,
                age=father_age,
                national_identifier=father_identifier.formatted_value if father_identifier else None,
                national_identifier_type=father_identifier.identifier_type if father_identifier else None,
            ),
            mother=ParentIdentity(
                full_name=mother_name,
                gender=Gender.FEMALE,
                age=mother_age,
                national_identifier=mother_identifier.formatted_value if mother_identifier else None,
                national_identifier_type=mother_identifier.identifier_type if mother_identifier else None,
            ),
        )

    def validate_parent_ages(self, *, child_age: int, family: Family) -> bool:
        return family.father.age >= child_age + 20 and family.mother.age >= child_age + 20

    def _parent_name(
        self,
        context: GenerationContext,
        *,
        pack: CountryPack,
        gender: Gender,
        surname_tail: str | None,
        avoid_surname: str | None = None,
    ) -> str:
        generated = self._name_generator.generate(
            context.child("name"),
            pack=pack,
            gender=gender,
            structure=NameStructure.FULL,
            rarity=Rarity.COMMON,
        )
        name_parts = generated.split()
        first_name = name_parts[0]
        resolved_surname = surname_tail or self._generated_surname(generated)
        if resolved_surname == avoid_surname:
            resolved_surname = self._alternate_surname(pack=pack, avoid=avoid_surname)
        return f"{first_name} {resolved_surname}"

    def _parent_surnames(self, *, pack: CountryPack, child_full_name: str) -> tuple[str | None, str | None]:
        parts = child_full_name.split()
        if not parts:
            return None, None
        if "double-surname" in pack.naming_style or "multi-surname" in pack.naming_style:
            if len(parts) >= 4:
                return parts[-1], parts[-2]
            if len(parts) >= 3:
                return parts[-1], parts[-2]
        surname = parts[-1]
        return surname, None

    def _generated_surname(self, full_name: str) -> str | None:
        parts = full_name.split()
        return parts[-1] if len(parts) >= 2 else None

    def _alternate_surname(self, *, pack: CountryPack, avoid: str | None) -> str:
        for surname in pack.surnames:
            if surname != avoid:
                return surname
        return avoid or "Synthetic"

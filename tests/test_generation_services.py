from synthetic_profiles.locales.countries.starter_packs import STARTER_PACKS
from synthetic_profiles.models.enums import AgeGroup, Gender, NameStructure, Rarity
from synthetic_profiles.models.schemas import GenerationRequest
from synthetic_profiles.services.age_generator import AgeGenerator
from synthetic_profiles.services.family_generator import FamilyGenerator
from synthetic_profiles.services.location_generator import LocationGenerator
from synthetic_profiles.services.name_generator import NameGenerator
from synthetic_profiles.services.password_generator import PasswordGenerator
from synthetic_profiles.utils.randomizer import GenerationContext


def ctx(seed: int | None = 1) -> GenerationContext:
    return GenerationContext.create(seed=seed)


def test_generation_request_validates_ranges() -> None:
    try:
        GenerationRequest(country_code="US", age_min=40, age_max=20)
    except ValueError:
        assert True
    else:
        assert False, "Expected validation error"


def test_name_generator_respects_structure_and_gender() -> None:
    generator = NameGenerator()
    pack = STARTER_PACKS["US"]

    male_name = generator.generate(
        ctx(1),
        pack=pack,
        gender=Gender.MALE,
        structure=NameStructure.FULL,
        rarity=Rarity.BALANCED,
    )
    female_name = generator.generate(
        ctx(2),
        pack=pack,
        gender=Gender.FEMALE,
        structure=NameStructure.FULL,
        rarity=Rarity.BALANCED,
    )

    assert len(male_name.split()) >= 2
    assert len(female_name.split()) >= 2
    assert male_name.split()[0] in pack.male_first_names
    assert female_name.split()[0] in pack.female_first_names


def test_age_generator_groups_are_correct() -> None:
    generator = AgeGenerator()

    assert generator.group_for(10) is AgeGroup.CHILD
    assert generator.group_for(16) is AgeGroup.TEENAGER
    assert generator.group_for(35) is AgeGroup.ADULT
    assert generator.group_for(72) is AgeGroup.ELDERLY


def test_age_generator_weights_favor_adult_ranges() -> None:
    generator = AgeGenerator()

    assert generator.age_weight(30) > generator.age_weight(16)
    assert generator.age_weight(30) > generator.age_weight(78)
    assert generator.age_weight(40) > generator.age_weight(10)


def test_location_generator_returns_only_country() -> None:
    location = LocationGenerator().generate(pack=STARTER_PACKS["BR"])

    assert location.country == "Brasil"
    assert location.country_code == "BR"


def test_bundled_name_pools_are_broad() -> None:
    br = STARTER_PACKS["BR"]
    us = STARTER_PACKS["US"]
    fr = STARTER_PACKS["FR"]

    assert len(br.male_first_names) == 900
    assert len(br.female_first_names) == 900
    assert len(br.surnames) == 900
    assert len(us.male_first_names) == 900
    assert len(us.female_first_names) == 900
    assert len(us.surnames) == 900
    assert len(fr.male_first_names) == 900
    assert len(fr.female_first_names) == 900
    assert len(fr.surnames) == 900


def test_password_generator_reports_length_and_entropy() -> None:
    password = PasswordGenerator().generate(ctx(6), length=24, exclude_ambiguous=True)

    assert len(password.value) == 24
    assert password.entropy_bits > 100
    assert password.strength == "very_strong"


def test_family_generator_returns_only_parents_and_they_are_older() -> None:
    family = FamilyGenerator(NameGenerator()).generate_parents(
        ctx(9),
        pack=STARTER_PACKS["FR"],
        child_age=28,
        child_full_name="Camille Mercier",
    )

    assert family.father.gender is Gender.MALE
    assert family.mother.gender is Gender.FEMALE
    assert family.father.age >= 48
    assert family.mother.age >= 48
    assert family.father.full_name.endswith("Mercier")
    assert not family.mother.full_name.endswith("Mercier")


def test_family_generator_splits_parent_surnames_for_multi_surname_locales() -> None:
    family = FamilyGenerator(NameGenerator()).generate_parents(
        ctx(11),
        pack=STARTER_PACKS["BR"],
        child_age=30,
        child_full_name="Paulo Murilo Almeida Rangel",
    )

    assert family.father.full_name.endswith("Rangel")
    assert family.mother.full_name.endswith("Almeida")


def test_family_generator_can_surface_parent_identifiers() -> None:
    from synthetic_profiles.identifiers.brazil_cpf import BrazilCPFGenerator

    cpf_generator = BrazilCPFGenerator()
    family = FamilyGenerator(NameGenerator()).generate_parents(
        ctx(12),
        pack=STARTER_PACKS["BR"],
        child_age=30,
        child_full_name="Paulo Murilo Almeida Rangel",
        father_identifier=cpf_generator.generate(ctx(12).rng("father-cpf")),
        mother_identifier=cpf_generator.generate(ctx(12).rng("mother-cpf")),
    )

    assert family.father.national_identifier is not None
    assert family.father.national_identifier_type == "cpf"
    assert family.mother.national_identifier is not None
    assert family.mother.national_identifier_type == "cpf"

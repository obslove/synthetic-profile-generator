import asyncio

from synthetic_profiles.bootstrap import build_profile_generator
from synthetic_profiles.config.settings import Settings
from synthetic_profiles.models.enums import Gender
from synthetic_profiles.models.schemas import BatchGenerationRequest, GenerationRequest


def test_non_seeded_runs_produce_different_outputs() -> None:
    generator = build_profile_generator(Settings())
    request = GenerationRequest(country_code="US", gender=Gender.FEMALE, use_simplelogin=False)

    first = asyncio.run(generator.generate_profile(request))
    second = asyncio.run(generator.generate_profile(request))

    assert first.randomness_metadata.deterministic_mode is False
    assert second.randomness_metadata.deterministic_mode is False
    assert first.randomness_metadata.generation_id != second.randomness_metadata.generation_id
    assert (
        first.identity.full_name != second.identity.full_name
        or first.credentials.email != second.credentials.email
        or first.credentials.password != second.credentials.password
    )


def test_generation_is_deterministic_with_seed() -> None:
    generator = build_profile_generator(Settings())
    request = GenerationRequest(country_code="US", gender=Gender.FEMALE, seed=77, use_simplelogin=False)

    first = asyncio.run(generator.generate_profile(request))
    second = asyncio.run(generator.generate_profile(request))

    assert first.identity == second.identity
    assert first.location == second.location
    assert first.family == second.family
    assert first.credentials == second.credentials
    assert first.randomness_metadata == second.randomness_metadata


def test_batch_generation_uses_different_batch_indexes_with_seed() -> None:
    generator = build_profile_generator(Settings())
    request = BatchGenerationRequest(
        count=3,
        country_code="US",
        gender=Gender.FEMALE,
        seed=42,
        use_simplelogin=False,
    )

    response = asyncio.run(generator.generate_batch(request))
    names = [profile.identity.full_name for profile in response.profiles]

    assert len(names) == 3
    assert len(set(names)) == len(names)


def test_optional_national_identifier_is_generated_for_br() -> None:
    generator = build_profile_generator(Settings())
    profile = asyncio.run(
        generator.generate_profile(
            GenerationRequest(
                country_code="BR",
                gender=Gender.MALE,
                seed=9,
                use_simplelogin=False,
                include_national_identifier=True,
            )
        )
    )

    assert profile.identity.national_identifier is not None
    assert profile.identity.national_identifier_type == "cpf"
    assert profile.family.father.national_identifier is not None
    assert profile.family.father.national_identifier_type == "cpf"
    assert profile.family.mother.national_identifier is not None
    assert profile.family.mother.national_identifier_type == "cpf"
    assert len(profile.synthetic_identifiers) == 3
    assert all(identifier.identifier_type == "cpf" for identifier in profile.synthetic_identifiers)
    assert profile.identity.national_identifier.count(".") == 2
    assert profile.identity.national_identifier.count("-") == 1


def test_optional_national_identifier_is_generated_for_supported_non_br_country() -> None:
    generator = build_profile_generator(Settings())
    profile = asyncio.run(
        generator.generate_profile(
            GenerationRequest(
                country_code="US",
                gender=Gender.FEMALE,
                seed=9,
                use_simplelogin=False,
                include_cpf=True,
            )
        )
    )

    assert len(profile.synthetic_identifiers) == 3
    assert profile.identity.national_identifier is not None
    assert profile.identity.national_identifier_type == "ssn_like"
    assert profile.family.father.national_identifier is not None
    assert profile.family.mother.national_identifier is not None
    assert not any("identifier generator" in warning.lower() for warning in profile.warnings)

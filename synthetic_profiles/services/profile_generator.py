from __future__ import annotations

from dataclasses import dataclass

from synthetic_profiles.identifiers.base import IdentifierGenerator
from synthetic_profiles.models.enums import NameStructure, Rarity
from synthetic_profiles.models.schemas import (
    BatchGenerationRequest,
    BatchGenerationResponse,
    Credentials,
    GenerationRequest,
    Identity,
    RandomnessMetadata,
    SyntheticProfile,
)
from synthetic_profiles.services.age_generator import AgeGenerator
from synthetic_profiles.services.email_generation import EmailGenerationService
from synthetic_profiles.services.family_generator import FamilyGenerator
from synthetic_profiles.services.gender_resolver import GenderResolver
from synthetic_profiles.services.locale_resolver import LocaleResolver
from synthetic_profiles.services.location_generator import LocationGenerator
from synthetic_profiles.services.name_generator import NameGenerator
from synthetic_profiles.services.password_generator import PasswordGenerator
from synthetic_profiles.utils.randomizer import GenerationContext


@dataclass(slots=True)
class ProfileGeneratorDependencies:
    locale_resolver: LocaleResolver
    gender_resolver: GenderResolver
    age_generator: AgeGenerator
    location_generator: LocationGenerator
    name_generator: NameGenerator
    family_generator: FamilyGenerator
    email_service: EmailGenerationService
    password_generator: PasswordGenerator
    identifier_generators: dict[tuple[str, str], IdentifierGenerator]


class ProfileGenerator:
    """Gera perfis sintéticos mínimos para testes e demonstrações."""

    IDENTIFIER_BY_COUNTRY = {
        "BR": "cpf",
        "US": "ssn_like",
    }

    def __init__(self, deps: ProfileGeneratorDependencies) -> None:
        self._deps = deps

    async def generate_profile(
        self,
        request: GenerationRequest,
        *,
        batch_index: int = 0,
    ) -> SyntheticProfile:
        locale_pack, pack_metadata = self._deps.locale_resolver.resolve(request.country_code)
        context = GenerationContext.create(seed=request.seed, batch_index=batch_index)
        gender = self._deps.gender_resolver.resolve(request.gender)
        age, _ = self._deps.age_generator.generate(context.child("age"), request.age_min, request.age_max)
        full_name = self._deps.name_generator.generate(
            context.child("name"),
            pack=locale_pack,
            gender=gender,
            structure=NameStructure.FULL,
            rarity=Rarity.COMMON,
        )
        self_identifier = None
        father_identifier = None
        mother_identifier = None
        identifiers = []
        if request.include_national_identifier:
            identifier_type = self.IDENTIFIER_BY_COUNTRY.get(request.country_code)
            generator = self._deps.identifier_generators.get((request.country_code, identifier_type)) if identifier_type else None
            if generator is not None:
                self_identifier = generator.generate(context.rng("identifier", "self"))
                father_identifier = generator.generate(context.rng("identifier", "father"))
                mother_identifier = generator.generate(context.rng("identifier", "mother"))
                identifiers.extend([self_identifier, father_identifier, mother_identifier])
        family = self._deps.family_generator.generate_parents(
            context.child("family"),
            pack=locale_pack,
            child_age=age,
            child_full_name=full_name,
            father_identifier=father_identifier,
            mother_identifier=mother_identifier,
        )
        emails, provider_metadata = await self._deps.email_service.generate_addresses(
            profile_name=full_name,
            count=1,
            use_simplelogin=request.use_simplelogin,
            context=context.child("emails"),
        )
        password = self._deps.password_generator.generate(
            context.child("password"),
            length=request.password_length,
            exclude_ambiguous=True,
        )
        warnings = list(pack_metadata.warnings)
        if provider_metadata.warning_message:
            warnings.append(provider_metadata.warning_message)
        if not emails:
            warnings.append("Nenhum endereço de e-mail foi gerado.")

        if request.include_national_identifier and not identifiers:
            warnings.append(
                "Não há gerador de identificador nacional sintético disponível para o país selecionado."
            )

        return SyntheticProfile(
            identity=Identity(
                full_name=full_name,
                gender=gender,
                age=age,
                national_identifier=self_identifier.formatted_value if self_identifier else None,
                national_identifier_type=self_identifier.identifier_type if self_identifier else None,
            ),
            location=self._deps.location_generator.generate(
                pack=locale_pack,
                state_query=request.state,
                city_query=request.city,
            ),
            family=family,
            credentials=Credentials(
                email=emails[0].address if emails else None,
                password=password.value,
            ),
            emails=emails,
            provider_metadata=provider_metadata,
            password=password,
            synthetic_identifiers=identifiers,
            randomness_metadata=RandomnessMetadata(
                deterministic_mode=context.deterministic_mode,
                seed_used=context.seed,
                generation_id=context.generation_id,
                rng_strategy=context.rng_strategy,
            ),
            country_pack_metadata=pack_metadata,
            warnings=warnings,
        )

    async def generate_batch(self, request: BatchGenerationRequest) -> BatchGenerationResponse:
        profiles: list[SyntheticProfile] = []
        warnings: list[str] = []
        for index in range(request.count):
            profile = await self.generate_profile(request, batch_index=index)
            profiles.append(profile)
            warnings.extend(profile.warnings)
        return BatchGenerationResponse(profiles=profiles, warnings=sorted(set(warnings)))

from __future__ import annotations

from synthetic_profiles.config.settings import Settings
from synthetic_profiles.identifiers.placeholders import build_identifier_generators
from synthetic_profiles.providers.fallback_email import FallbackEmailProvider
from synthetic_profiles.providers.simplelogin import SimpleLoginProvider
from synthetic_profiles.services.age_generator import AgeGenerator
from synthetic_profiles.services.country_registry import CountryRegistry
from synthetic_profiles.services.email_generation import EmailGenerationService
from synthetic_profiles.services.family_generator import FamilyGenerator
from synthetic_profiles.services.gender_resolver import GenderResolver
from synthetic_profiles.services.locale_resolver import LocaleResolver
from synthetic_profiles.services.name_generator import NameGenerator
from synthetic_profiles.services.password_generator import PasswordGenerator
from synthetic_profiles.services.profile_generator import ProfileGenerator, ProfileGeneratorDependencies


def build_profile_generator(settings: Settings | None = None) -> ProfileGenerator:
    settings = settings or Settings()
    registry = CountryRegistry()
    locale_resolver = LocaleResolver(registry)
    name_generator = NameGenerator()
    simplelogin_provider = (
        SimpleLoginProvider(
            api_key=settings.simplelogin_api_key,
            base_url=settings.simplelogin_base_url,
            timeout_seconds=settings.request_timeout_seconds,
        )
        if settings.simplelogin_api_key
        else None
    )
    deps = ProfileGeneratorDependencies(
        locale_resolver=locale_resolver,
        gender_resolver=GenderResolver(),
        age_generator=AgeGenerator(),
        name_generator=name_generator,
        family_generator=FamilyGenerator(name_generator),
        email_service=EmailGenerationService(
            simplelogin_provider=simplelogin_provider,
            fallback_provider=FallbackEmailProvider(settings.fallback_email_domains),
        ),
        password_generator=PasswordGenerator(),
        identifier_generators=build_identifier_generators(
            strict_identifier_safety_mode=settings.strict_identifier_safety_mode
        ),
    )
    return ProfileGenerator(deps)

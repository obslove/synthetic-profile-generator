from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from synthetic_profiles.models.enums import EmailProviderName, Gender, ResponseMode


class CountryPackMetadata(BaseModel):
    country_code: str
    country_name: str
    languages: list[str]
    naming_style: str
    fallback_used: bool = False
    warnings: list[str] = Field(default_factory=list)


class Identity(BaseModel):
    full_name: str
    gender: Gender
    age: int
    national_identifier: str | None = None
    national_identifier_type: str | None = None


class Location(BaseModel):
    country: str
    country_code: str


class ParentIdentity(BaseModel):
    full_name: str
    gender: Gender
    age: int
    national_identifier: str | None = None
    national_identifier_type: str | None = None


class Family(BaseModel):
    father: ParentIdentity
    mother: ParentIdentity


class ProviderMetadata(BaseModel):
    provider_selected: EmailProviderName
    fallback_occurred: bool = False
    warning_message: str | None = None
    retries_attempted: int = 0
    degraded_mode: bool = False
    simplelogin_requested: bool = False
    provider_reason: str | None = None
    provider_reason_code: str | None = None


class GeneratedEmail(BaseModel):
    address: str
    provider: EmailProviderName
    is_alias: bool = False
    metadata: dict[str, str | int | bool | None] = Field(default_factory=dict)


class Credentials(BaseModel):
    email: str | None = None
    password: str | None = None


class SyntheticIdentifier(BaseModel):
    value: str
    formatted_value: str
    country_code: str
    identifier_type: str
    is_synthetic_identifier: Literal[True] = True
    safe_for_testing_only: Literal[True] = True


class RandomnessMetadata(BaseModel):
    deterministic_mode: bool
    seed_used: int | None = None
    generation_id: str
    rng_strategy: str
    output_version: str = "3.0"


class GeneratedPassword(BaseModel):
    value: str
    length: int
    entropy_bits: float
    strength: str


class SyntheticProfile(BaseModel):
    identity: Identity
    location: Location
    family: Family
    credentials: Credentials
    emails: list[GeneratedEmail] = Field(default_factory=list)
    provider_metadata: ProviderMetadata
    password: GeneratedPassword
    synthetic_identifiers: list[SyntheticIdentifier] = Field(default_factory=list)
    randomness_metadata: RandomnessMetadata
    country_pack_metadata: CountryPackMetadata
    warnings: list[str] = Field(default_factory=list)


class GenerationRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=False)

    country_code: str = "US"
    gender: Gender = Gender.FEMALE
    age_min: int = 16
    age_max: int = 78
    password_length: int = 24
    use_simplelogin: bool = True
    include_cpf: bool = True
    seed: int | None = None
    debug_output: bool = False
    response_mode: ResponseMode = ResponseMode.CLEAN

    @field_validator("country_code")
    @classmethod
    def normalize_country_code(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if len(cleaned) != 2 or not cleaned.isalpha():
            raise ValueError("country_code must be an ISO 3166-1 alpha-2 code")
        return cleaned

    @model_validator(mode="after")
    def validate_ranges(self) -> "GenerationRequest":
        if self.age_min > self.age_max:
            raise ValueError("age_min must be <= age_max")
        if self.password_length < 12:
            raise ValueError("password_length must be >= 12")
        return self


class BatchGenerationRequest(GenerationRequest):
    count: int = 10

    @field_validator("count")
    @classmethod
    def validate_count(cls, value: int) -> int:
        if value < 1:
            raise ValueError("count must be >= 1")
        return value


class BatchGenerationResponse(BaseModel):
    profiles: list[SyntheticProfile]
    warnings: list[str] = Field(default_factory=list)

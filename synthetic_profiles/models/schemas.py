from __future__ import annotations

from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator, model_validator

from synthetic_profiles.locales.countries.cities import city_choices, resolve_city
from synthetic_profiles.locales.countries.subdivisions import (
    resolve_subdivision,
    subdivision_choices,
    subdivision_type_for,
)
from synthetic_profiles.models.enums import EmailProviderName, Gender, ResponseMode


class CountryPackMetadata(BaseModel):
    country_code: str
    country_name: str
    languages: list[str]
    naming_style: str
    subdivision_type: str | None = None
    subdivision_types: list[str] = Field(default_factory=list)
    subdivision_count: int = 0
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
    state: str | None = None
    state_code: str | None = None
    state_type: str | None = None
    city: str | None = None


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
    model_config = ConfigDict(use_enum_values=False, populate_by_name=True)

    country_code: str = "US"
    gender: Gender = Gender.FEMALE
    age_min: int = 16
    age_max: int = 78
    password_length: int = 24
    state: str | None = None
    city: str | None = None
    use_simplelogin: bool = True
    include_national_identifier: bool = Field(
        default=True,
        validation_alias=AliasChoices("include_national_identifier", "include_cpf"),
        serialization_alias="include_national_identifier",
    )
    seed: int | None = None
    debug_output: bool = False
    response_mode: ResponseMode = ResponseMode.CLEAN

    @model_validator(mode="before")
    @classmethod
    def validate_identifier_aliases(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        include_national_identifier = data.get("include_national_identifier")
        include_cpf = data.get("include_cpf")
        if (
            include_national_identifier is not None
            and include_cpf is not None
            and include_national_identifier != include_cpf
        ):
            raise ValueError(
                "include_national_identifier e include_cpf não podem ter valores diferentes"
            )
        return data

    @field_validator("country_code")
    @classmethod
    def normalize_country_code(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if len(cleaned) != 2 or not cleaned.isalpha():
            raise ValueError("country_code deve ser um código ISO 3166-1 alpha-2")
        return cleaned

    @field_validator("state")
    @classmethod
    def normalize_state(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("city")
    @classmethod
    def normalize_city(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @model_validator(mode="after")
    def validate_ranges(self) -> "GenerationRequest":
        if self.age_min > self.age_max:
            raise ValueError("age_min deve ser <= age_max")
        if self.password_length < 12:
            raise ValueError("password_length deve ser >= 12")
        if self.state is not None:
            subdivision = resolve_subdivision(self.country_code, self.state)
            if subdivision is None:
                label = subdivision_type_for(self.country_code)
                if label in {None, "mixed"}:
                    label = "subdivisão"
                raise ValueError(
                    f"{label} não suportado para {self.country_code}: {self.state}. "
                    f"Valores aceitos: {subdivision_choices(self.country_code)}"
                )
        if self.city is not None:
            if self.state is None:
                raise ValueError("city exige uma subdivisão em state")
            subdivision = resolve_subdivision(self.country_code, self.state)
            if subdivision is None:
                raise ValueError("state inválido para a city informada")
            city = resolve_city(self.country_code, subdivision.code, self.city)
            if city is None:
                choices = city_choices(self.country_code, subdivision.code)
                if not choices:
                    raise ValueError(
                        f"não há catálogo de cidades para {self.country_code}/{subdivision.code}"
                    )
                raise ValueError(
                    f"city não suportada para {self.country_code}/{subdivision.code}: {self.city}. "
                    f"Valores aceitos: {choices}"
                )
        return self

    @property
    def include_cpf(self) -> bool:
        return self.include_national_identifier


class BatchGenerationRequest(GenerationRequest):
    count: int = 10

    @field_validator("count")
    @classmethod
    def validate_count(cls, value: int) -> int:
        if value < 1:
            raise ValueError("count deve ser >= 1")
        return value


class BatchGenerationResponse(BaseModel):
    profiles: list[SyntheticProfile]
    warnings: list[str] = Field(default_factory=list)

from __future__ import annotations

import json

from synthetic_profiles.models.schemas import BatchGenerationResponse, SyntheticProfile


class OutputFormatter:
    """Render simplified profile data for JSON and CLI output."""

    def _identifier_label(self, identifier_type: str | None) -> str:
        if identifier_type == "cpf":
            return "CPF"
        if identifier_type == "ssn_like":
            return "SSN-like"
        if identifier_type == "nir_like":
            return "NIR-like"
        return "National ID"

    def format_profile(
        self,
        profile: SyntheticProfile,
        *,
        debug: bool = False,
        legacy: bool = False,
        include_cli_hints: bool = False,
    ) -> dict[str, object]:
        if legacy:
            return profile.model_dump(mode="json")
        payload: dict[str, object] = {
            "identity": profile.identity.model_dump(mode="json"),
            "location": profile.location.model_dump(mode="json"),
            "family": {
                "father": profile.family.father.model_dump(mode="json"),
                "mother": profile.family.mother.model_dump(mode="json"),
            },
            "credentials": profile.credentials.model_dump(mode="json"),
        }
        if include_cli_hints:
            provider_summary = None
            if profile.provider_metadata.fallback_occurred:
                provider_summary = (
                    f"{profile.provider_metadata.provider_selected.value}"
                    + (
                        f" ({profile.provider_metadata.provider_reason_code})"
                        if profile.provider_metadata.provider_reason_code
                        else ""
                    )
                )
            payload["_cli"] = {"email_provider_summary": provider_summary}
        if debug:
            payload["debug"] = {
                "provider": {
                    "provider_used": profile.provider_metadata.provider_selected.value,
                    "fallback_occurred": profile.provider_metadata.fallback_occurred,
                    "reason": profile.provider_metadata.provider_reason,
                    "reason_code": profile.provider_metadata.provider_reason_code,
                },
                "generation": profile.randomness_metadata.model_dump(mode="json"),
                "warnings": profile.warnings,
            }
        return payload

    def format_batch(
        self,
        response: BatchGenerationResponse,
        *,
        debug: bool = False,
        legacy: bool = False,
        include_cli_hints: bool = False,
    ) -> dict[str, object]:
        if legacy:
            return response.model_dump(mode="json")
        payload: dict[str, object] = {
            "profiles": [
                self.format_profile(
                    profile,
                    debug=debug,
                    legacy=False,
                    include_cli_hints=include_cli_hints,
                )
                for profile in response.profiles
            ]
        }
        if debug:
            payload["debug"] = {"warnings": response.warnings, "count": len(response.profiles)}
        return payload

    def to_json(self, data: dict[str, object], *, pretty: bool = True) -> str:
        return json.dumps(data, indent=2 if pretty else None, ensure_ascii=False)

    def to_pretty_text(self, payload: dict[str, object], *, debug: bool = False) -> str:
        if "profiles" in payload:
            chunks = []
            for index, profile in enumerate(payload["profiles"], start=1):
                chunks.append(f"Profile {index}\n{self.to_pretty_text(profile, debug=debug)}")
            return "\n\n".join(chunks)

        identity = payload["identity"]
        location = payload["location"]
        family = payload["family"]
        credentials = payload["credentials"]
        cli_hints = payload.get("_cli", {})
        lines = [
            "Identity",
            f"  Name: {identity['full_name']}",
            f"  Gender: {identity['gender']}",
            f"  Age: {identity['age']}",
            *(
                [
                    f"  {self._identifier_label(identity.get('national_identifier_type'))}: {identity['national_identifier']}"
                ]
                if identity.get("national_identifier")
                else []
            ),
            "",
            "Location",
            f"  Country: {location['country']} ({location['country_code']})",
            "",
            "Family",
            f"  Father: {family['father']['full_name']} | {family['father']['gender']} | {family['father']['age']}"
            + (
                f" | {self._identifier_label(family['father'].get('national_identifier_type'))} {family['father']['national_identifier']}"
                if family["father"].get("national_identifier")
                else ""
            ),
            f"  Mother: {family['mother']['full_name']} | {family['mother']['gender']} | {family['mother']['age']}"
            + (
                f" | {self._identifier_label(family['mother'].get('national_identifier_type'))} {family['mother']['national_identifier']}"
                if family["mother"].get("national_identifier")
                else ""
            ),
            "",
            "Credentials",
            f"  Email: {credentials['email'] or 'not generated'}",
            f"  Password: {credentials['password'] or 'not generated'}",
            *(
                [f"  Email Provider: {cli_hints['email_provider_summary']}"]
                if cli_hints.get("email_provider_summary")
                else []
            ),
        ]
        if debug and "debug" in payload:
            lines.extend(
                [
                    "",
                    "Debug",
                    f"  Provider: {payload['debug']['provider']['provider_used']}",
                    f"  Fallback: {payload['debug']['provider']['fallback_occurred']}",
                    f"  Reason: {payload['debug']['provider']['reason_code']}",
                    f"  Deterministic: {payload['debug']['generation']['deterministic_mode']}",
                    f"  Seed: {payload['debug']['generation']['seed_used']}",
                    f"  Generation ID: {payload['debug']['generation']['generation_id']}",
                ]
            )
        return "\n".join(lines)

    def to_compact_text(self, payload: dict[str, object], *, debug: bool = False) -> str:
        if "profiles" in payload:
            return "\n\n".join(self.to_compact_text(profile, debug=debug) for profile in payload["profiles"])
        identity = payload["identity"]
        location = payload["location"]
        credentials = payload["credentials"]
        cli_hints = payload.get("_cli", {})
        lines = [
            f"{identity['full_name']} | {identity['gender']} | {identity['age']}",
            f"{location['country']} ({location['country_code']})",
            f"Email: {credentials['email'] or 'not generated'}",
            f"Password: {credentials['password'] or 'not generated'}",
        ]
        if cli_hints.get("email_provider_summary"):
            lines.append(f"Email Provider: {cli_hints['email_provider_summary']}")
        if identity.get("national_identifier"):
            lines.append(
                f"{self._identifier_label(identity.get('national_identifier_type'))}: {identity['national_identifier']}"
            )
        if debug and "debug" in payload:
            provider = payload["debug"]["provider"]
            lines.append(f"Provider: {provider['provider_used']} | fallback={provider['fallback_occurred']} | reason={provider['reason_code']}")
        return "\n".join(lines)

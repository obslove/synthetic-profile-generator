from __future__ import annotations

import json

from synthetic_profiles.models.schemas import BatchGenerationResponse, SyntheticProfile


class OutputFormatter:
    """Renderiza dados simplificados do perfil para JSON e saída de CLI."""

    def _location_label(self, state_type: str | None) -> str:
        if state_type == "region":
            return "Região"
        if state_type == "department":
            return "Departamento"
        if state_type == "territory":
            return "Território"
        if state_type == "district":
            return "Distrito"
        if state_type == "collectivity":
            return "Coletividade"
        return "Estado"

    def _identifier_label(self, identifier_type: str | None) -> str:
        if identifier_type == "cpf":
            return "CPF"
        if identifier_type == "ssn_like":
            return "SSN-like"
        return "Identificador nacional"

    def format_countries(self, countries: list[dict[str, object]]) -> dict[str, object]:
        return {"countries": countries}

    def format_subdivisions(
        self,
        subdivisions: list[dict[str, str]],
        *,
        country_code: str,
        country_name: str,
    ) -> dict[str, object]:
        return {
            "subdivisions": subdivisions,
            "_cli": {
                "country_code": country_code,
                "country_name": country_name,
            },
        }

    def format_cities(
        self,
        cities: list[dict[str, str | bool]],
        *,
        country_code: str,
        country_name: str,
        subdivision_code: str,
        subdivision_name: str,
        subdivision_type: str,
    ) -> dict[str, object]:
        return {
            "cities": cities,
            "_cli": {
                "country_code": country_code,
                "country_name": country_name,
                "subdivision_code": subdivision_code,
                "subdivision_name": subdivision_name,
                "subdivision_type": subdivision_type,
            },
        }

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
        if "countries" in payload:
            lines = ["Países"]
            for item in payload["countries"]:
                subdivision_types = ", ".join(item.get("subdivision_types", []))
                lines.append(
                    f"  {item['country_name']} ({item['country_code']}) | "
                    f"subdivisões: {item['subdivision_count']}"
                    + (f" | tipos: {subdivision_types}" if subdivision_types else "")
                )
            return "\n".join(lines)

        if "subdivisions" in payload:
            cli_hints = payload.get("_cli", {})
            lines = [
                "Subdivisões",
                f"  País: {cli_hints.get('country_name')} ({cli_hints.get('country_code')})",
            ]
            for item in payload["subdivisions"]:
                lines.append(
                    f"  {self._location_label(item.get('type'))}: {item['name']} ({item['code']})"
                )
            return "\n".join(lines)

        if "cities" in payload:
            cli_hints = payload.get("_cli", {})
            lines = [
                "Cidades",
                f"  País: {cli_hints.get('country_name')} ({cli_hints.get('country_code')})",
                f"  {self._location_label(cli_hints.get('subdivision_type'))}: "
                f"{cli_hints.get('subdivision_name')} ({cli_hints.get('subdivision_code')})",
            ]
            for item in payload["cities"]:
                lines.append(
                    f"  Cidade: {item['name']}" + (" | capital" if item.get("is_capital") else "")
                )
            return "\n".join(lines)

        if "profiles" in payload:
            chunks = []
            for index, profile in enumerate(payload["profiles"], start=1):
                chunks.append(f"Perfil {index}\n{self.to_pretty_text(profile, debug=debug)}")
            return "\n\n".join(chunks)

        identity = payload["identity"]
        location = payload["location"]
        family = payload["family"]
        credentials = payload["credentials"]
        cli_hints = payload.get("_cli", {})
        lines = [
            "Identidade",
            f"  Nome: {identity['full_name']}",
            f"  Gênero: {identity['gender']}",
            f"  Idade: {identity['age']}",
            *(
                [
                    f"  {self._identifier_label(identity.get('national_identifier_type'))}: {identity['national_identifier']}"
                ]
                if identity.get("national_identifier")
                else []
            ),
            "",
            "Localização",
            f"  País: {location['country']} ({location['country_code']})",
            *(
                [
                    f"  {self._location_label(location.get('state_type'))}: "
                    f"{location['state']} ({location['state_code']})"
                ]
                if location.get("state")
                else []
            ),
            *([f"  Cidade: {location['city']}"] if location.get("city") else []),
            "",
            "Família",
            f"  Pai: {family['father']['full_name']} | {family['father']['gender']} | {family['father']['age']}"
            + (
                f" | {self._identifier_label(family['father'].get('national_identifier_type'))} {family['father']['national_identifier']}"
                if family["father"].get("national_identifier")
                else ""
            ),
            f"  Mãe: {family['mother']['full_name']} | {family['mother']['gender']} | {family['mother']['age']}"
            + (
                f" | {self._identifier_label(family['mother'].get('national_identifier_type'))} {family['mother']['national_identifier']}"
                if family["mother"].get("national_identifier")
                else ""
            ),
            "",
            "Credenciais",
            f"  E-mail: {credentials['email'] or 'não gerado'}",
            f"  Senha: {credentials['password'] or 'não gerada'}",
            *(
                [f"  Provedor de e-mail: {cli_hints['email_provider_summary']}"]
                if cli_hints.get("email_provider_summary")
                else []
            ),
        ]
        if debug and "debug" in payload:
            lines.extend(
                [
                    "",
                    "Depuração",
                    f"  Provedor: {payload['debug']['provider']['provider_used']}",
                    f"  Fallback: {payload['debug']['provider']['fallback_occurred']}",
                    f"  Motivo: {payload['debug']['provider']['reason_code']}",
                    f"  Determinístico: {payload['debug']['generation']['deterministic_mode']}",
                    f"  Seed: {payload['debug']['generation']['seed_used']}",
                    f"  ID de geração: {payload['debug']['generation']['generation_id']}",
                ]
            )
        return "\n".join(lines)

    def to_compact_text(self, payload: dict[str, object], *, debug: bool = False) -> str:
        if "countries" in payload:
            return "\n".join(
                (
                    f"{item['country_code']} | {item['country_name']} | "
                    f"{item['subdivision_count']} | {', '.join(item.get('subdivision_types', []))}"
                )
                for item in payload["countries"]
            )

        if "subdivisions" in payload:
            return "\n".join(
                f"{item['code']} | {item['name']} | {item['type']}"
                for item in payload["subdivisions"]
            )

        if "cities" in payload:
            return "\n".join(
                f"{item['name']} | capital={item['is_capital']}"
                for item in payload["cities"]
            )

        if "profiles" in payload:
            return "\n\n".join(self.to_compact_text(profile, debug=debug) for profile in payload["profiles"])
        identity = payload["identity"]
        location = payload["location"]
        credentials = payload["credentials"]
        cli_hints = payload.get("_cli", {})
        lines = [
            f"{identity['full_name']} | {identity['gender']} | {identity['age']}",
            f"{location['country']} ({location['country_code']})",
            *(
                [
                    f"{self._location_label(location.get('state_type'))}: "
                    f"{location['state']} ({location['state_code']})"
                ]
                if location.get("state")
                else []
            ),
            f"E-mail: {credentials['email'] or 'não gerado'}",
            f"Senha: {credentials['password'] or 'não gerada'}",
        ]
        if cli_hints.get("email_provider_summary"):
            lines.append(f"Provedor de e-mail: {cli_hints['email_provider_summary']}")
        if identity.get("national_identifier"):
            lines.append(
                f"{self._identifier_label(identity.get('national_identifier_type'))}: {identity['national_identifier']}"
            )
        if debug and "debug" in payload:
            provider = payload["debug"]["provider"]
            lines.append(
                f"Provedor: {provider['provider_used']} | fallback={provider['fallback_occurred']} | motivo={provider['reason_code']}"
            )
        return "\n".join(lines)

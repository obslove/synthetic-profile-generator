from __future__ import annotations


class SyntheticProfileError(Exception):
    """Erro base da aplicação."""


class UnsupportedCountryError(SyntheticProfileError):
    """Disparado quando um código de país não é válido para a aplicação."""


class EmailProviderError(SyntheticProfileError):
    """Disparado quando a geração de e-mail via provedor falha."""

    def __init__(self, message: str, *, reason_code: str = "provider_error") -> None:
        super().__init__(message)
        self.reason_code = reason_code

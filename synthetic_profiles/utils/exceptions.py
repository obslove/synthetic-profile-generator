from __future__ import annotations


class SyntheticProfileError(Exception):
    """Base application error."""


class UnsupportedCountryError(SyntheticProfileError):
    """Raised when a country code is not ISO-valid."""


class EmailProviderError(SyntheticProfileError):
    """Raised when email generation via a provider fails."""

    def __init__(self, message: str, *, reason_code: str = "provider_error") -> None:
        super().__init__(message)
        self.reason_code = reason_code

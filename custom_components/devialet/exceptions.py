"""Exceptions raised by the Devialet API client."""

from __future__ import annotations


class DevialetError(Exception):
    """Base exception for Devialet failures."""


class DevialetConnectionError(DevialetError):
    """Raised when the device cannot be reached."""


class DevialetResponseError(DevialetError):
    """Raised when the device returned an HTTP or API error."""

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        code: str | None = None,
    ) -> None:
        """Initialize the exception."""
        super().__init__(message)
        self.status = status
        self.code = code

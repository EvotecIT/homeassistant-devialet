"""Compatibility wrapper for reusable Devialet exceptions."""

from .devialet_client import (
    DevialetConnectionError,
    DevialetError,
    DevialetResponseError,
)

__all__ = [
    "DevialetConnectionError",
    "DevialetError",
    "DevialetResponseError",
]

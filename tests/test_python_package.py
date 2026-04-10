"""Regression checks for the standalone Devialet Python package."""

from devialet_client import DevialetApiClient
from devialet_client.client import DevialetApiClient as ClientFromModule


def test_public_package_exports_client() -> None:
    assert DevialetApiClient is ClientFromModule

"""Minimal standalone example for the reusable Devialet client package."""

from __future__ import annotations

import asyncio
import os

from aiohttp import ClientSession

from devialet_client import DevialetApiClient


async def main() -> None:
    host = os.environ.get("DEVIALET_HOST", "192.168.1.10")

    async with ClientSession() as session:
        client = DevialetApiClient(host, session)
        snapshot = await client.async_refresh()

    print(f"Device: {snapshot.device.device_name}")
    print(f"System: {snapshot.system.system_name}")
    source = snapshot.source_state.source if snapshot.source_state else "unknown"
    print(f"Source: {source}")
    print(f"Volume: {snapshot.volume.level if snapshot.volume else 'unknown'}")


if __name__ == "__main__":
    asyncio.run(main())

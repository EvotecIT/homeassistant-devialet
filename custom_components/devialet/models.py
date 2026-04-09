"""Typed models for the Devialet IP Control API."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class DevialetReleaseInfo:
    """Firmware release information."""

    version: str | None = None
    canonical_version: str | None = None
    build_type: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, object] | None) -> DevialetReleaseInfo:
        """Build release info from API payload."""
        payload = payload or {}
        return cls(
            version=_as_str(payload.get("version")),
            canonical_version=_as_str(payload.get("canonicalVersion")),
            build_type=_as_str(payload.get("buildType")),
        )


@dataclass(slots=True, frozen=True)
class DevialetDeviceInfo:
    """Device information."""

    device_id: str | None
    device_name: str | None
    serial: str | None
    model: str | None
    model_family: str | None
    firmware_family: str | None
    ip_control_version: str | None
    installation_id: str | None
    group_id: str | None
    system_id: str | None
    role: str | None
    setup_state: str | None
    available_features: frozenset[str] = field(default_factory=frozenset)
    release: DevialetReleaseInfo = field(default_factory=DevialetReleaseInfo)

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> DevialetDeviceInfo:
        """Build device info from API payload."""
        return cls(
            device_id=_as_str(payload.get("deviceId")),
            device_name=_as_str(payload.get("deviceName")),
            serial=_as_str(payload.get("serial")),
            model=_as_str(payload.get("model")),
            model_family=_as_str(payload.get("modelFamily")),
            firmware_family=_as_str(payload.get("firmwareFamily")),
            ip_control_version=_as_str(payload.get("ipControlVersion")),
            installation_id=_as_str(payload.get("installationId")),
            group_id=_as_str(payload.get("groupId")),
            system_id=_as_str(payload.get("systemId")),
            role=_as_str(payload.get("role")),
            setup_state=_as_str(payload.get("setupState")),
            available_features=frozenset(
                _as_str_list(payload.get("availableFeatures"))
            ),
            release=DevialetReleaseInfo.from_dict(_as_dict(payload.get("release"))),
        )


@dataclass(slots=True, frozen=True)
class DevialetSystemInfo:
    """System information."""

    system_id: str | None
    system_name: str | None
    system_type: str | None
    group_id: str | None
    is_group_leader: bool | None
    available_features: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> DevialetSystemInfo:
        """Build system info from API payload."""
        return cls(
            system_id=_as_str(payload.get("systemId")),
            system_name=_as_str(payload.get("systemName")),
            system_type=_as_str(payload.get("systemType")),
            group_id=_as_str(payload.get("groupId")),
            is_group_leader=_as_bool(payload.get("isGroupLeader")),
            available_features=frozenset(
                _as_str_list(payload.get("availableFeatures"))
            ),
        )


@dataclass(slots=True, frozen=True)
class DevialetSource:
    """A source entry."""

    source_id: str
    device_id: str | None
    type: str
    stream_lock_available: bool | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> DevialetSource:
        """Build source info from API payload."""
        return cls(
            source_id=_as_str(payload.get("sourceId")) or "",
            device_id=_as_str(payload.get("deviceId")),
            type=_as_str(payload.get("type")) or "unknown",
            stream_lock_available=_as_bool(payload.get("streamLockAvailable")),
        )


@dataclass(slots=True, frozen=True)
class DevialetMetadata:
    """Current media metadata."""

    artist: str | None = None
    album: str | None = None
    title: str | None = None
    duration: int | None = None
    media_type: str | None = None
    cover_art_url: str | None = None
    cover_art_data_present: bool | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, object] | None) -> DevialetMetadata | None:
        """Build metadata from API payload."""
        if not payload:
            return None
        return cls(
            artist=_as_str(payload.get("artist")),
            album=_as_str(payload.get("album")),
            title=_as_str(payload.get("title")),
            duration=_as_int(payload.get("duration")),
            media_type=_as_str(payload.get("mediaType")),
            cover_art_url=_as_str(payload.get("coverArtUrl")),
            cover_art_data_present=_as_bool(payload.get("coverArtDataPresent")),
        )


@dataclass(slots=True, frozen=True)
class DevialetStreamInfo:
    """Technical information about the current stream."""

    codec: str | None = None
    channels: str | None = None
    sampling_rate: int | None = None
    bit_depth: int | None = None
    lossless: bool | None = None
    supported: bool | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, object] | None) -> DevialetStreamInfo | None:
        """Build stream info from API payload."""
        if not payload:
            return None
        return cls(
            codec=_as_str(payload.get("codec")),
            channels=_as_str(payload.get("channels")),
            sampling_rate=_as_int(payload.get("samplingRate")),
            bit_depth=_as_int(payload.get("bitDepth")),
            lossless=_as_bool(payload.get("lossless")),
            supported=_as_bool(payload.get("supported")),
        )


@dataclass(slots=True, frozen=True)
class DevialetSourceState:
    """Current playback state."""

    source: DevialetSource | None
    playing_state: str | None
    mute_state: str | None
    available_operations: tuple[str, ...]
    metadata: DevialetMetadata | None
    stream_info: DevialetStreamInfo | None
    stream_lock: bool | None
    peer_device_name: str | None

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> DevialetSourceState:
        """Build source state from API payload."""
        source_payload = _as_dict(payload.get("source"))
        return cls(
            source=DevialetSource.from_dict(source_payload) if source_payload else None,
            playing_state=_as_str(payload.get("playingState")),
            mute_state=_as_str(payload.get("muteState")),
            available_operations=tuple(
                _as_str_list(payload.get("availableOperations"))
            ),
            metadata=DevialetMetadata.from_dict(_as_dict(payload.get("metadata"))),
            stream_info=DevialetStreamInfo.from_dict(
                _as_dict(payload.get("streamInfo"))
            ),
            stream_lock=_as_bool(payload.get("streamLock")),
            peer_device_name=_as_str(payload.get("peerDeviceName")),
        )


@dataclass(slots=True, frozen=True)
class DevialetVolume:
    """Volume state."""

    volume: int | None

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> DevialetVolume:
        """Build volume from API payload."""
        return cls(volume=_as_int(payload.get("volume")))


@dataclass(slots=True, frozen=True)
class DevialetNightMode:
    """Night mode state."""

    night_mode: bool

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> DevialetNightMode:
        """Build night mode from API payload."""
        return cls(night_mode=_as_str(payload.get("nightMode")) == "on")


@dataclass(slots=True, frozen=True)
class DevialetRenderingMode:
    """Rendering mode state."""

    rendering_mode: str | None
    available_rendering_modes: tuple[str, ...]

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> DevialetRenderingMode:
        """Build rendering mode from API payload."""
        return cls(
            rendering_mode=_as_str(payload.get("renderingMode")),
            available_rendering_modes=tuple(
                _as_str_list(payload.get("availableRenderingModes"))
            ),
        )


@dataclass(slots=True, frozen=True)
class DevialetLedMode:
    """LED mode state."""

    led_mode: str | None
    led_control: str | None

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> DevialetLedMode:
        """Build LED mode from API payload."""
        return cls(
            led_mode=_as_str(payload.get("ledMode")),
            led_control=_as_str(payload.get("ledControl")),
        )


@dataclass(slots=True, frozen=True)
class DevialetPowerManagement:
    """Power management state."""

    auto_power_off: str | None
    auto_power_off_period: int | None

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> DevialetPowerManagement:
        """Build power-management state from API payload."""
        return cls(
            auto_power_off=_as_str(payload.get("autoPowerOff")),
            auto_power_off_period=_as_int(payload.get("autoPowerOffPeriod")),
        )


@dataclass(slots=True, frozen=True)
class DevialetSnapshot:
    """A full coordinator snapshot."""

    device: DevialetDeviceInfo
    system: DevialetSystemInfo
    sources: tuple[DevialetSource, ...]
    source_state: DevialetSourceState | None
    volume: DevialetVolume | None
    night_mode: DevialetNightMode | None
    rendering_mode: DevialetRenderingMode | None
    led_mode: DevialetLedMode | None
    power_management: DevialetPowerManagement | None


def _as_dict(value: object) -> dict[str, object] | None:
    """Return a dict value if possible."""
    return value if isinstance(value, dict) else None


def _as_str(value: object) -> str | None:
    """Return a string value if possible."""
    return value if isinstance(value, str) else None


def _as_int(value: object) -> int | None:
    """Return an int value if possible."""
    return value if isinstance(value, int) else None


def _as_bool(value: object) -> bool | None:
    """Return a bool value if possible."""
    return value if isinstance(value, bool) else None


def _as_str_list(value: object) -> list[str]:
    """Return a list of strings."""
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]

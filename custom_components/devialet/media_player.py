"""Media player platform for Devialet."""

from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.components.media_player.const import MediaType

from .const import build_source_option_map, source_label
from .entity import DevialetCoordinatorEntity

BASE_FEATURES = (
    MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_STEP
)

OPERATION_FEATURE_MAP = {
    "play": MediaPlayerEntityFeature.PLAY | MediaPlayerEntityFeature.STOP,
    "pause": MediaPlayerEntityFeature.PAUSE,
    "next": MediaPlayerEntityFeature.NEXT_TRACK,
    "previous": MediaPlayerEntityFeature.PREVIOUS_TRACK,
    "seek": MediaPlayerEntityFeature.SEEK,
}


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up the Devialet media player."""
    async_add_entities([DevialetMediaPlayer(entry.runtime_data)])


class DevialetMediaPlayer(DevialetCoordinatorEntity, MediaPlayerEntity):
    """Representation of a Devialet system as a Home Assistant media player."""

    _attr_name = None

    def __init__(self, coordinator) -> None:
        """Initialize the media player."""
        super().__init__(coordinator, "media_player")

    @property
    def state(self) -> MediaPlayerState | None:
        """Return the current player state."""
        source_state = self.coordinator.data.source_state
        if source_state is None or source_state.playing_state is None:
            return MediaPlayerState.IDLE
        if source_state.playing_state == "playing":
            return MediaPlayerState.PLAYING
        if source_state.playing_state == "paused":
            return MediaPlayerState.PAUSED
        return MediaPlayerState.ON

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Return supported media-player features."""
        features = BASE_FEATURES
        source_state = self.coordinator.data.source_state
        if source_state is None:
            return features
        for operation in source_state.available_operations:
            features |= OPERATION_FEATURE_MAP.get(operation, 0)
        return features

    @property
    def source_list(self) -> list[str]:
        """Return available source labels."""
        return list(
            build_source_option_map(
                (source.type, source.source_id)
                for source in self.coordinator.data.sources
            )
        )

    @property
    def source(self) -> str | None:
        """Return the current source label."""
        source_state = self.coordinator.data.source_state
        if source_state is None or source_state.source is None:
            return None
        option_map = build_source_option_map(
            (source.type, source.source_id) for source in self.coordinator.data.sources
        )
        for label, source_id in option_map.items():
            if source_id == source_state.source.source_id:
                return label
        return source_label(source_state.source.type)

    @property
    def volume_level(self) -> float | None:
        """Return the current volume level."""
        volume = self.coordinator.data.volume
        if volume is None or volume.volume is None:
            return None
        return volume.volume / 100

    @property
    def is_volume_muted(self) -> bool | None:
        """Return whether the device is muted."""
        source_state = self.coordinator.data.source_state
        if source_state is None:
            return None
        return source_state.mute_state == "muted"

    @property
    def media_artist(self) -> str | None:
        """Return the media artist."""
        metadata = (
            self.coordinator.data.source_state.metadata
            if self.coordinator.data.source_state
            else None
        )
        return metadata.artist if metadata else None

    @property
    def media_album_name(self) -> str | None:
        """Return the current album name."""
        metadata = (
            self.coordinator.data.source_state.metadata
            if self.coordinator.data.source_state
            else None
        )
        return metadata.album if metadata else None

    @property
    def media_title(self) -> str | None:
        """Return the current media title."""
        metadata = (
            self.coordinator.data.source_state.metadata
            if self.coordinator.data.source_state
            else None
        )
        if metadata and metadata.title:
            return metadata.title
        return self.source

    @property
    def media_duration(self) -> int | None:
        """Return the media duration."""
        metadata = (
            self.coordinator.data.source_state.metadata
            if self.coordinator.data.source_state
            else None
        )
        return metadata.duration if metadata else None

    @property
    def media_image_url(self) -> str | None:
        """Return the artwork URL."""
        metadata = (
            self.coordinator.data.source_state.metadata
            if self.coordinator.data.source_state
            else None
        )
        return metadata.cover_art_url if metadata else None

    @property
    def media_content_type(self) -> MediaType:
        """Return the media type."""
        return MediaType.MUSIC

    async def async_set_volume_level(self, volume: float) -> None:
        """Set the player volume."""
        await self._async_perform(
            self.coordinator.client.async_set_volume_level(volume)
        )

    async def async_volume_up(self) -> None:
        """Raise the volume."""
        await self._async_perform(self.coordinator.client.async_volume_up())

    async def async_volume_down(self) -> None:
        """Lower the volume."""
        await self._async_perform(self.coordinator.client.async_volume_down())

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute or unmute the player."""
        if mute:
            await self._async_perform(self.coordinator.client.async_mute())
            return
        await self._async_perform(self.coordinator.client.async_unmute())

    async def async_media_play(self) -> None:
        """Play media."""
        await self._async_perform(self.coordinator.client.async_play())

    async def async_media_pause(self) -> None:
        """Pause media."""
        await self._async_perform(self.coordinator.client.async_pause())

    async def async_media_stop(self) -> None:
        """Stop media."""
        await self._async_perform(self.coordinator.client.async_stop())

    async def async_media_next_track(self) -> None:
        """Go to the next track."""
        await self._async_perform(self.coordinator.client.async_next_track())

    async def async_media_previous_track(self) -> None:
        """Go to the previous track."""
        await self._async_perform(self.coordinator.client.async_previous_track())

    async def async_media_seek(self, position: float) -> None:
        """Seek to a position."""
        await self._async_perform(self.coordinator.client.async_seek(int(position)))

    async def async_select_source(self, source: str) -> None:
        """Select a source."""
        source_map = build_source_option_map(
            (item.type, item.source_id) for item in self.coordinator.data.sources
        )
        source_id = source_map[source]
        await self._async_perform(
            self.coordinator.client.async_select_source(source_id)
        )

    async def async_turn_off(self) -> None:
        """Turn off the system."""
        await self._async_perform(self.coordinator.client.async_turn_off())

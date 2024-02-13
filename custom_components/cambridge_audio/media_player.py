"""Support for Cambridge Audio AV Receiver."""
from __future__ import annotations

from async_stream_magic import StreamMagicError

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import CambridgeAudioCoordinator

PARALLEL_UPDATES = 1

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Elgato Light based on a config entry."""
    coordinator: CambridgeAudioCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([CambridgeAudio(coordinator)])

class CambridgeAudio(CoordinatorEntity[CambridgeAudioCoordinator], MediaPlayerEntity):
    """Representation of a Cambridge Audio Media Player Device."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, coordinator: CambridgeAudioCoordinator) -> None:
        """Initialize an Cambridge Audio entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers = {(DOMAIN, coordinator.data.info.unit_id)},
            serial_number = coordinator.data.info.unit_id,
            manufacturer = "Cambridge Audio",
            model = coordinator.data.info.model,
            name = coordinator.data.info.name)
        self._attr_unique_id = coordinator.data.info.unit_id
        self._attr_supported_features = (
            MediaPlayerEntityFeature.SELECT_SOURCE
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_MUTE
            | MediaPlayerEntityFeature.VOLUME_STEP
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.TURN_ON)

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return "mdi:audio-video"

    @property
    def state(self):
        """Return the state of the device."""
        if self.coordinator.data.state.power:
            return STATE_ON
        return STATE_OFF

    @property
    def source_list(self):
        """Return a list of available input sources."""
        return [item.name for item in self.coordinator.data.sources]

    @property
    def is_volume_muted(self):
        """Return boolean if volume is currently muted."""
        return self.coordinator.data.state.mute

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        volume_percent = self.coordinator.data.state.volume_percent
        if volume_percent is None:
            return None
        return float(volume_percent) / 100

    @property
    def source(self):
        """Return the current input source."""
        return next((item.name for item in self.coordinator.data.sources if item.id == self.coordinator.data.state.source), None)
        #return self.coordinator.data.state.source

    async def async_mute_volume(self, mute):
        """Send mute command."""
        try:
            if mute:
                await self.coordinator.client.set_volume_mute_on()
            else:
                await self.coordinator.client.set_volume_mute_off()
        except StreamMagicError as error:
            raise HomeAssistantError(
            "An error occurred while updating the Elgato Light"
        ) from error
        finally:
            await self.coordinator.async_refresh()

    async def async_turn_on(self):
        """Turn the media player on."""
        try:
            await self.coordinator.client.set_power_on()
        except StreamMagicError as error:
            raise HomeAssistantError(
            "An error occurred while updating the Elgato Light"
        ) from error
        finally:
            await self.coordinator.async_refresh()

    async def async_turn_off(self):
        """Turn the media player off."""
        try:
            await self.coordinator.client.set_power_off()
        except StreamMagicError as error:
            raise HomeAssistantError(
            "An error occurred while updating the Elgato Light"
        ) from error
        finally:
            await self.coordinator.async_refresh()

    async def async_set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        try:
            await self.coordinator.client.set_volume_percent(int(volume * 100))
        except StreamMagicError as error:
            raise HomeAssistantError(
            "An error occurred while updating the Elgato Light"
        ) from error
        finally:
            await self.coordinator.async_refresh()

    async def async_volume_up(self):
        """Set volume level step up."""
        try:
            await self.coordinator.client.set_volume_step_up()
        except StreamMagicError as error:
            raise HomeAssistantError(
            "An error occurred while updating the Elgato Light"
        ) from error
        finally:
            await self.coordinator.async_refresh()

    async def async_volume_down(self):
        """Set volume level step down."""
        try:
            await self.coordinator.client.set_volume_step_down()
        except StreamMagicError as error:
            raise HomeAssistantError(
            "An error occurred while updating the Elgato Light"
        ) from error
        finally:
            await self.coordinator.async_refresh()

    async def async_select_source(self, source):
        """Select input source."""
        try:
            source_object = next((item for item in self.coordinator.data.sources if item.name == source), None)
            await self.coordinator.client.set_source(source_object)
        except StreamMagicError as error:
            raise HomeAssistantError(
            "An error occurred while updating the Elgato Light"
        ) from error
        finally:
            await self.coordinator.async_refresh()

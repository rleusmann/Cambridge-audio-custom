"""DataUpdateCoordinator for Cambridge Audio."""

from dataclasses import dataclass

from async_stream_magic import Info, Source, State, StreamMagic, StreamMagicError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, SCAN_INTERVAL


@dataclass
class CambridgeAudioData:
    """CambridgeAudio data stored in the DataUpdateCoordinator."""

    info: Info
    sources: list[Source]
    state: State

class CambridgeAudioCoordinator(DataUpdateCoordinator[CambridgeAudioData]):
    """Cambridge Audio Coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize my coordinator."""
        self.config_entry = entry
        self.client = StreamMagic(
            entry.data[CONF_HOST],
            session=async_get_clientsession(hass),
        )
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_{entry.data[CONF_HOST]}",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> CambridgeAudioData:
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            return CambridgeAudioData(
                info = await self.client.get_info(),
                sources = await self.client.get_sources(),
                state = await self.client.get_state(),
            )
        except StreamMagicError as err:
            raise UpdateFailed(err) from err

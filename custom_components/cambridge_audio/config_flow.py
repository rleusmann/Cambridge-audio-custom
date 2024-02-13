"""Config flow for Cambridge Audio integration."""
from __future__ import annotations

from typing import Any

from async_stream_magic import StreamMagic, StreamMagicError
import voluptuous as vol

from homeassistant.components import onboarding, zeroconf
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN


class CambridgeAudioFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a Cambridge Audio Device config flow."""

    VERSION = 1

    host: str
    unit_id: str

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
        ) -> FlowResult:
            """Handle a flow initiated by the user."""
            if user_input is None:
                return self._async_show_setup_form()

            self.host = user_input[CONF_HOST]

            try:
                await self._get_serial_number(raise_on_progress=False)
            except StreamMagicError:
                return self._async_show_setup_form({"base": "cannot_connect"})

            return self._async_create_entry()


    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle zeroconf discovery."""
        self.host = discovery_info.host
        self.unit_id = discovery_info.properties.get("serial")

        try:
            await self._get_serial_number()
        except StreamMagicError:
            return self.async_abort(reason="cannot_connect")

        if not onboarding.async_is_onboarded(self.hass):
            return self._async_create_entry()

        self._set_confirm_only()
        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={"serial_number": self.unit_id},
        )

    async def async_step_zeroconf_confirm(
        self, _: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by zeroconf."""
        return self._async_create_entry()

    @callback
    def _async_show_setup_form(
        self, errors: dict[str, str] | None = None
    ) -> FlowResult:
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                }
            ),
            errors=errors or {},
        )

    @callback
    def _async_create_entry(self) -> FlowResult:
        return self.async_create_entry(
            title = self.unit_id,
            data = {
                CONF_HOST: self.host,
            },
        )

    async def _get_serial_number(self, raise_on_progress: bool = True) -> None:
        """Get device information from an Elgato Light device."""
        session = async_get_clientsession(self.hass)
        streamMagic = StreamMagic(
            host=self.host,
            session=session,
        )
        info = await streamMagic.get_info()

        # Check if already configured
        await self.async_set_unique_id(info.unit_id)
        self._abort_if_unique_id_configured(
            updates={CONF_HOST: self.host,}
        )
        self.unit_id = info.unit_id

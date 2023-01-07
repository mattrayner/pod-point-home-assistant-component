"""Adds config flow for Pod Point."""
from typing import Any
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.components import dhcp
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import (
    CONF_HOST,
    CONF_MAC,
    CONF_NAME,
)
import voluptuous as vol

from podpointclient.client import PodPointClient

from .const import (
    CONF_HTTP_DEBUG,
    CONF_PASSWORD,
    CONF_EMAIL,
    DEFAULT_HTTP_DEBUG,
    DOMAIN,
    PLATFORMS,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    CONF_CURRENCY,
    DEFAULT_CURRENCY,
)


class PodPointFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Pod Point."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    # pylint: disable=unused-argument
    async def async_step_reauth(self, user_input=None):
        """Perform reauth upon an API authentication error."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=vol.Schema({}),
            )
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        # if self._async_current_entries():
        #     return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            user_input = {}
            # Provide defaults for form
            user_input[CONF_EMAIL] = ""
            user_input[CONF_PASSWORD] = ""

            return await self._show_config_form(user_input)

        valid = await self._test_credentials(
            user_input[CONF_EMAIL], user_input[CONF_PASSWORD]
        )

        if valid is False:
            self._errors["base"] = "auth"
            return await self._show_config_form(user_input)

        existing_entry = await self.async_set_unique_id(user_input[CONF_EMAIL].lower())

        # If an entry exists, update it and show the re-auth message
        if existing_entry:
            self.hass.config_entries.async_update_entry(
                existing_entry, title=user_input[CONF_EMAIL], data=user_input
            )
            await self.hass.config_entries.async_reload(existing_entry.entry_id)
            return self.async_abort(reason="reauth_successful")

        return self.async_create_entry(title=user_input[CONF_EMAIL], data=user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PodPointOptionsFlowHandler(config_entry)

    async def async_step_dhcp(self, discovery_info: dhcp.DhcpServiceInfo) -> FlowResult:
        """Prepare configuration for a DHCP discovered PodPoint device."""
        return await self._process_discovered_device(
            {
                CONF_HOST: discovery_info.ip,
                CONF_MAC: discovery_info.macaddress,
                CONF_NAME: discovery_info.hostname,
            }
        )

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL, default=user_input[CONF_EMAIL]): str,
                    vol.Required(CONF_PASSWORD, default=user_input[CONF_PASSWORD]): str,
                }
            ),
            errors=self._errors,
        )

    async def _test_credentials(self, username, password):
        """Return true if credentials is valid."""
        try:
            session = async_create_clientsession(self.hass)
            client = PodPointClient(
                username=username, password=password, session=session
            )
            return await client.async_credentials_verified()
        except Exception:  # pylint: disable=broad-except
            pass
        return False

    async def _process_discovered_device(self, device: dict[str, Any]) -> FlowResult:
        """Prepare configuration for a discovered Axis device."""
        # if device[CONF_MAC][:8] not in AXIS_OUI:
        #     return self.async_abort(reason="not_axis_device")

        # if is_link_local(ip_address(device[CONF_HOST])):
        #     return self.async_abort(reason="link_local_address")

        # await self.async_set_unique_id(device[CONF_MAC])

        # self._abort_if_unique_id_configured(
        #     updates={
        #         CONF_HOST: device[CONF_HOST],
        #         CONF_PORT: device[CONF_PORT],
        #     }
        # )

        # self.context.update(
        #     {
        #         "title_placeholders": {
        #             CONF_NAME: device[CONF_NAME],
        #             CONF_HOST: device[CONF_HOST],
        #         },
        #         "configuration_url": f"http://{device[CONF_HOST]}:{device[CONF_PORT]}",
        #     }
        # )

        self.discovery_schema = {
            vol.Required(CONF_HOST, default=device[CONF_HOST]): str,
            vol.Required(CONF_EMAIL): str,
            vol.Required(CONF_PASSWORD): str,
        }

        return await self.async_step_user()


class PodPointOptionsFlowHandler(config_entries.OptionsFlow):
    """Pod Point config flow options handler."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        currency_schema = {
            vol.Required(
                CONF_CURRENCY,
                default=self.options.get(CONF_CURRENCY, DEFAULT_CURRENCY),
            ): str
        }

        poll_schema = {
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=self.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): int
        }

        platforms_schema = {
            vol.Required(
                x,
                default=self.options.get(x, True),
            ): bool
            for x in sorted(PLATFORMS)
        }

        debug_schema = {
            vol.Required(
                CONF_HTTP_DEBUG,
                default=self.options.get(CONF_HTTP_DEBUG, DEFAULT_HTTP_DEBUG),
            ): bool
        }

        options_schema = vol.Schema(
            {**currency_schema, **poll_schema, **platforms_schema, **debug_schema}
        )

        return self.async_show_form(step_id="user", data_schema=options_schema)

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_EMAIL), data=self.options
        )

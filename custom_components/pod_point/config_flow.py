"""Adds config flow for Blueprint."""
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import voluptuous as vol

from podpointclient.client import PodPointClient

from .const import (
    CONF_PASSWORD,
    CONF_EMAIL,
    DOMAIN,
    PLATFORMS,
    ENERGY,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)


class BlueprintFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

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

        if user_input is not None:
            valid = await self._test_credentials(
                user_input[CONF_EMAIL], user_input[CONF_PASSWORD]
            )

            if valid:
                existing_entry = await self.async_set_unique_id(DOMAIN)
                if existing_entry:
                    self.hass.config_entries.async_update_entry(
                        existing_entry, title=user_input[CONF_EMAIL], data=user_input
                    )
                    await self.hass.config_entries.async_reload(existing_entry.entry_id)

                return self.async_create_entry(
                    title=user_input[CONF_EMAIL], data=user_input
                )
            else:
                self._errors["base"] = "auth"

            return await self._show_config_form(user_input)

        user_input = {}
        # Provide defaults for form
        user_input[CONF_EMAIL] = ""
        user_input[CONF_PASSWORD] = ""

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PodPointOptionsFlowHandler(config_entry)

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
            await client.async_get_pods()
            return True
        except Exception:  # pylint: disable=broad-except
            pass
        return False


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

        options_schema = vol.Schema({**poll_schema, **platforms_schema})

        return self.async_show_form(step_id="user", data_schema=options_schema)

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_EMAIL), data=self.options
        )

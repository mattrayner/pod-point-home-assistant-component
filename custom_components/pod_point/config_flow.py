"""Adds config flow for Pod Point."""

import logging
from typing import Dict

from homeassistant import config_entries
from homeassistant.helpers.service_info.dhcp import DhcpServiceInfo
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType
from podpointclient.client import PodPointClient
from podpointclient.errors import MfaError, MfaInvalidCode, MfaRequired
import voluptuous as vol

from .const import (
    CONF_CURRENCY,
    CONF_EMAIL,
    CONF_HTTP_DEBUG,
    CONF_PASSWORD,
    CONF_REFRESH_TOKEN,
    CONF_SCAN_INTERVAL,
    DEFAULT_CURRENCY,
    DEFAULT_HTTP_DEBUG,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)


class PodPointFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Pod Point."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}
        self._mfa_client: PodPointClient | None = None

    # pylint: disable=unused-argument
    async def async_step_reauth(self, user_input: Dict[str, str] = None) -> FlowResult:
        """Perform reauth upon an API authentication error."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: Dict[str, str] = None
    ) -> FlowResult:
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=vol.Schema({}),
            )
        return await self.async_step_user()

    async def async_step_user(self, user_input: Dict[str, str] = None) -> FlowResult:
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is None:
            email = ""
            if self.source == config_entries.SOURCE_REAUTH:
                email = self._get_reauth_entry().data[CONF_EMAIL]
            return await self._show_config_form(email)

        email = user_input[CONF_EMAIL].strip()
        if (
            self.source == config_entries.SOURCE_REAUTH
            and email.lower() != self._get_reauth_entry().data[CONF_EMAIL].lower()
        ):
            return self.async_abort(reason="wrong_account")

        client = PodPointClient(
            username=email,
            password=user_input[CONF_PASSWORD],
            session=async_get_clientsession(self.hass),
        )
        try:
            valid = await client.async_credentials_verified()
        except MfaRequired:
            try:
                await client.auth.async_start_mfa()
            except MfaError:
                self._errors["base"] = "mfa_start"
                return await self._show_config_form(email)
            self._mfa_client = client
            return await self.async_step_mfa()
        except Exception:  # pylint: disable=broad-except
            valid = False

        if not valid:
            self._errors["base"] = "auth"
            return await self._show_config_form(email)

        return await self._async_finish_login(client)

    async def async_step_mfa(self, user_input=None) -> FlowResult:
        """Complete two-step verification with the code sent by text."""
        client = self._mfa_client
        if client is None:
            return self.async_abort(reason="mfa_expired")

        errors = {}
        if user_input is not None:
            try:
                if await client.auth.async_complete_mfa(user_input["code"].strip()):
                    if await client.async_credentials_verified():
                        self._mfa_client = None
                        return await self._async_finish_login(
                            client, refresh_token=client.auth.refresh_token
                        )
            except MfaInvalidCode:
                errors["base"] = "mfa_code"
            except Exception:  # pylint: disable=broad-except
                pass

            if not errors:
                self._mfa_client = None
                self._errors["base"] = "mfa_failed"
                return await self._show_config_form(client.email)

        return self.async_show_form(
            step_id="mfa",
            data_schema=vol.Schema({
                vol.Required("code"): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD)
                )
            }),
            errors=errors,
        )

    async def _async_finish_login(
        self, client: PodPointClient, refresh_token: str | None = None
    ) -> FlowResult:
        data = {CONF_EMAIL: client.email, CONF_PASSWORD: client.password}
        if refresh_token:
            data[CONF_REFRESH_TOKEN] = refresh_token
        if self.source == config_entries.SOURCE_REAUTH:
            return self.async_update_reload_and_abort(
                self._get_reauth_entry(), data=data
            )
        await self.async_set_unique_id(client.email.lower())
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=client.email, data=data)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> FlowResult:
        return PodPointOptionsFlowHandler(config_entry)

    async def async_step_dhcp(self, discovery_info: DhcpServiceInfo) -> FlowResult:
        formatted_mac = format_mac(discovery_info.macaddress)
        _LOGGER.info("Found PodPoint device with mac %s", formatted_mac)

        await self.async_set_unique_id(formatted_mac)
        self._abort_if_unique_id_configured()

        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        return await self.async_step_user()

    async def _show_config_form(self, email: str) -> FlowResult:
        """Show the login form."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL, default=email): str,
                    vol.Required(CONF_PASSWORD): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                }
            ),
            errors=self._errors,
        )


class PodPointOptionsFlowHandler(config_entries.OptionsFlow):
    """Pod Point config flow options handler."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(
        self, _=None
    ) -> FlowResult:  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None) -> FlowResult:
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
            {**currency_schema, **platforms_schema, **debug_schema, **poll_schema}
        )

        return self.async_show_form(step_id="user", data_schema=options_schema)

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_EMAIL), data=self.options
        )

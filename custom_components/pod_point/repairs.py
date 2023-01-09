"""Repairs implementation for the cloud integration."""
from __future__ import annotations

import asyncio
from typing import Any

from hass_nabucasa import Cloud
import voluptuous as vol

from homeassistant.components.repairs import RepairsFlow, repairs_flow_manager
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN

BACKOFF_TIME = 5
MAX_RETRIES = 60  # This allows for 10 minutes of retries


# @callback
# def async_manage_legacy_subscription_issue(
#     hass: HomeAssistant,
#     subscription_info: dict[str, Any],
# ) -> None:
#     """
#     Manage the legacy subscription issue.
#     If the provider is "legacy" create an issue,
#     in all other cases remove the issue.
#     """
#     if subscription_info.get("provider") == "legacy":
#         ir.async_create_issue(
#             hass=hass,
#             domain=DOMAIN,
#             issue_id="legacy_subscription",
#             is_fixable=True,
#             severity=ir.IssueSeverity.WARNING,
#             translation_key="legacy_subscription",
#         )
#         return
#     ir.async_delete_issue(hass=hass, domain=DOMAIN, issue_id="legacy_subscription")


class FirmwareUpdateRepairFlow(RepairsFlow):
    """Handler for an issue fixing flow."""

    async def async_step_init(self, _: None = None) -> FlowResult:
        """Handle the first step of a fix flow."""
        return await self.async_step_mobile_app_prompt()

    async def async_step_mobile_app_prompt(
        self,
        user_input: dict[str, str] | None = None,
    ) -> FlowResult:
        """Handle the confirm step of a fix flow."""
        if user_input is not None:
            return self.async_abort(reason="continue_in_app")
            # return self.async_external_step_done(next_step_id="complete")

        return self.async_show_form(
            step_id="mobile_app_prompt", data_schema=vol.Schema({})
        )

    # def confirm_app(self)

    async def async_step_complete(self, _: None = None) -> FlowResult:
        """Handle the final step of a fix flow."""
        return self.async_abort(reason="continue_in_app")


async def async_create_fix_flow(
    _: HomeAssistant,
    __: str,
    ___: dict[str, str | int | float | None] | None,
) -> RepairsFlow:
    """Create flow."""
    return FirmwareUpdateRepairFlow()

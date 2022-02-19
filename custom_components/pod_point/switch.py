"""Switch platform for integration_blueprint."""
from homeassistant.components.switch import SwitchEntity

import logging
from .const import DEFAULT_NAME, DOMAIN, ICON, SWITCH
from .entity import PodPointEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    switches = []
    for i in range(len(coordinator.data)):
        switch = PodPointBinarySwitch(coordinator, entry)
        switch.pod_id = i

        switches.append(switch)
    async_add_devices(switches)


class PodPointBinarySwitch(PodPointEntity, SwitchEntity):
    """pod_point switch class."""

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Allow charging (clear schedule)"""
        await self.coordinator.api.async_set_schedule(False, self.unit_id)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Block charging (turn on schedule)"""
        await self.coordinator.api.async_set_schedule(True, self.unit_id)
        await self.coordinator.async_request_refresh()

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{DEFAULT_NAME}_{SWITCH}"

    @property
    def icon(self):
        """Return the icon of this switch."""
        return ICON

    @property
    def is_on(self):
        """Return true if the switch is on."""
        _LOGGER.info("is_on called")
        return self.charging_allowed

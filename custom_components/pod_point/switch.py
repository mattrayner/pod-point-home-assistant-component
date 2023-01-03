"""Switch platform for pod_point."""
import logging

from homeassistant.components.switch import SwitchEntity
from podpointclient.client import PodPointClient

from .const import DOMAIN, SWITCH_ICON
from .entity import PodPointEntity
from .coordinator import PodPointDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator: PodPointDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    # Handle coordinator offline on boot - no data will be populated
    if coordinator.online is False:
        return

    switches = []

    for i in range(len(coordinator.data)):
        switch = PodPointBinarySwitch(coordinator, entry, i)

        switches.append(switch)
    async_add_devices(switches)


class PodPointBinarySwitch(PodPointEntity, SwitchEntity):
    """pod_point switch class."""

    _attr_has_entity_name = True
    _attr_name = "Charging Allowed"
    _attr_icon = SWITCH_ICON

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Allow charging (clear schedule)"""
        api: PodPointClient = self.coordinator.api
        await api.async_set_schedule(enabled=False, pod=self.pod)

        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Block charging (turn on schedule)"""
        api: PodPointClient = self.coordinator.api
        await api.async_set_schedule(enabled=True, pod=self.pod)

        await self.coordinator.async_request_refresh()

    @property
    def unique_id(self):
        return f"{super().unique_id}_charging_allowed"

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self.charging_allowed

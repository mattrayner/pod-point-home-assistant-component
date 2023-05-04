"""Binary sensor platform for pod_point."""
import logging
from typing import Any, Dict

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from .const import ATTR_STATE, DOMAIN
from .coordinator import PodPointDataUpdateCoordinator
from .entity import PodPointEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup binary_sensor platform."""
    coordinator: PodPointDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    # Handle coordinator offline on boot - no data will be populated
    if coordinator.online is False:
        return

    sensors = []
    for i in range(len(coordinator.data)):
        sensor = PodPointBinarySensor(coordinator, entry, i)
        sensor.pod_id = i
        sensors.append(sensor)

    async_add_devices(sensors)


class PodPointBinarySensor(PodPointEntity, BinarySensorEntity):
    """pod_point binary_sensor class."""

    _attr_has_entity_name = True
    _attr_name = "Cable Status"
    _attr_device_class = BinarySensorDeviceClass.PLUG

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        state = super().extra_state_attributes.get(ATTR_STATE, "")
        return {
            ATTR_STATE: state,
            "current_kwhs": self.pod.current_kwh,
        }

    @property
    def unique_id(self):
        return f"{super().unique_id}_cable_status"

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self.connected

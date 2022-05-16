"""Binary sensor platform for integration_blueprint."""
import logging
from typing import Dict, Any

from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import (
    ATTR_STATE,
    BINARY_SENSOR_DEVICE_CLASS,
    DOMAIN,
)
from .entity import PodPointEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []
    for i in range(len(coordinator.data)):
        sensor = PodPointBinarySensor(coordinator, entry, i)
        sensor.pod_id = i
        sensors.append(sensor)

    async_add_devices(sensors)


class PodPointBinarySensor(PodPointEntity, BinarySensorEntity):
    """integration_blueprint binary_sensor class."""

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
    def name(self) -> str:
        return f"{self.pod.ppid} Cable Status"

    @property
    def device_class(self):
        """Return the class of this binary_sensor."""
        return BINARY_SENSOR_DEVICE_CLASS

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self.connected

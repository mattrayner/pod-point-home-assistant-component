"""Binary sensor platform for integration_blueprint."""
import logging
from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import (
    ATTR_STATE,
    ATTR_STATE_CONNECTED_WAITING,
    BINARY_SENSOR_DEVICE_CLASS,
    DOMAIN,
    CHARGING_FLAG,
)
from .entity import PodPointEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []
    for i in range(len(coordinator.data)):
        sensor = PodPointBinarySensor(coordinator, entry)
        sensor.pod_id = i
        sensors.append(sensor)

    async_add_devices([sensor])


class PodPointBinarySensor(PodPointEntity, BinarySensorEntity):
    """integration_blueprint binary_sensor class."""

    @property
    def name(self):
        """Return the name of the binary_sensor."""
        return "Cable Status"

    @property
    def device_class(self):
        """Return the class of this binary_sensor."""
        return BINARY_SENSOR_DEVICE_CLASS

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        status = self.extra_state_attributes.get(ATTR_STATE, "")

        _LOGGER.debug(
            "Looking for flag '%s' or '%s'",
            CHARGING_FLAG,
            ATTR_STATE_CONNECTED_WAITING,
        )
        _LOGGER.debug("Got state '%s'", status)

        return status in (CHARGING_FLAG, ATTR_STATE_CONNECTED_WAITING)

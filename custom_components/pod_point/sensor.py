"""Sensor platform for integration_blueprint."""
import logging
from typing_extensions import Self
from homeassistant.components.sensor import SensorEntity

from .const import (
    ATTR_MODEL,
    ATTR_STATE,
    DEFAULT_NAME,
    DOMAIN,
    ICON,
    ICON_1C,
    ICON_2C,
    SENSOR,
    ATTR_IMAGE,
)
from .entity import PodPointEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = []

    for i in range(len(coordinator.data)):
        sensor = PodPointSensor(coordinator, entry)
        sensor.pod_id = i
        sensors.append(sensor)

    async_add_devices(sensors)


class PodPointSensor(
    PodPointEntity,
    SensorEntity,
):
    """integration_blueprint Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Pod Status"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        _LOGGER.info("Native value")
        _LOGGER.info(self.extra_state_attributes[ATTR_STATE])
        return self.extra_state_attributes[ATTR_STATE]

    @property
    def icon(self):
        """Return the icon of the sensor."""
        model_slug = self.model.upper()[3:8].split("-")
        model_type = model_slug[0]

        if model_type == "1C":
            return ICON_1C

        if model_type == "2C":
            return ICON_2C

        if model_type == "UC":
            return ICON

        return ICON

    @property
    def entity_picture(self) -> str:
        return self.image

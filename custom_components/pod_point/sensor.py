"""Sensor platform for integration_blueprint."""
import logging
from homeassistant.components.sensor import SensorEntity
from typing import Dict, Any

from datetime import datetime, timedelta, timezone

from homeassistant.components.sensor import (
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntity,
)

from .entity import PodPointEntity
from homeassistant.const import (
    ENERGY_KILO_WATT_HOUR,
    DEVICE_CLASS_ENERGY,
)

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
from .entity import PodPointEntity, NAME

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = []

    for i in range(len(coordinator.data)):
        pps = PodPointSensor(coordinator, entry, i)
        pptes = PodPointTotalEnergySensor(coordinator, entry, i)
        ppces = PodPointCurrentEnergySensor(coordinator, entry, i)

        sensors.append(pps)
        sensors.append(pptes)
        sensors.append(ppces)

    async_add_devices(sensors)


class PodPointSensor(
    PodPointEntity,
    SensorEntity,
):
    """integration_blueprint Sensor class."""

    @property
    def device_class(self) -> str:
        return f"{DOMAIN}__pod"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Pod Status"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.extra_state_attributes.get(ATTR_STATE, None)

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


class PodPointTotalEnergySensor(PodPointSensor):
    """pod_point total energy Sensor class."""

    @property
    def unique_id(self):
        return f"{super().unique_id}_total_energy"

    @property
    def name(self) -> str:
        return f"{self.pod.ppid} Total Energy"

    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_ENERGY

    @property
    def state_class(self) -> str:
        return STATE_CLASS_TOTAL_INCREASING

    @property
    def native_value(self) -> float:
        return self.pod.total_kwh

    @property
    def native_unit_of_measurement(self) -> str:
        return ENERGY_KILO_WATT_HOUR

    @property
    def last_reset(self) -> datetime:
        charges_count = len(self.pod.charges) - 1
        if charges_count <= 0:
            return datetime.now(tz=timezone.utc)

        return self.pod.charges[charges_count].starts_at - timedelta(seconds=10)

    @property
    def icon(self):
        icon = "mdi:lightning-bolt-outline"

        if self.connected:
            icon = "mdi:lightning-bolt"

        return icon

    @property
    def entity_picture(self) -> str:
        return None

    @property
    def is_on(self) -> bool:
        return self.connected


class PodPointCurrentEnergySensor(PodPointTotalEnergySensor):
    """pod_point current charge energy Sensor class."""

    @property
    def unique_id(self):
        return f"{super().unique_id}_current_charge_energy"

    @property
    def name(self) -> str:
        return f"{self.pod.ppid} Current Energy"

    @property
    def native_value(self) -> float:
        return self.pod.current_kwh

    @property
    def last_reset(self) -> datetime:
        if len(self.pod.charges) <= 0:
            return datetime.now(tz=timezone.utc)

        charge = self.pod.charges[0]
        return charge.starts_at - timedelta(seconds=10)

    @property
    def icon(self):
        icon = "mdi:car"

        if self.connected:
            icon = "mdi:car-electric"

        return icon

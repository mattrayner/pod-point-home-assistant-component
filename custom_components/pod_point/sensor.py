"""Sensor platform for integration_blueprint."""
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from typing import Dict, Any
from homeassistant.core import callback
from podpointclient.pod import Pod
from .const import ATTRIBUTION, DOMAIN

from datetime import datetime, timedelta, timezone

from homeassistant.components.sensor import (
    STATE_CLASS_TOTAL,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntity,
)

from .entity import PodPointEntity
from homeassistant.const import (
    ENERGY_KILO_WATT_HOUR,
    DEVICE_CLASS_ENERGY,
)

from .const import (
    ATTR_STATE,
    DOMAIN,
    ICON,
    ICON_1C,
    ICON_2C,
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
    def unique_id(self):
        return f"{super().unique_id}_status"

    @property
    def name(self) -> str:
        return f"{self.pod.ppid} Status"

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

    def __init__(self, coordinator, config_entry: ConfigEntry, idx: int):
        super().__init__(coordinator, config_entry=config_entry, idx=idx)
        self.previous_total = self.pod.total_kwh
        self.total_kwh_diff = self.previous_total

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.__update_attrs()
        self.async_write_ha_state()

    def __update_attrs(self):
        pod: Pod = self.pod

        new_total = self.pod.total_kwh
        self.total_kwh_diff = new_total - self.previous_total
        self.previous_total = new_total

        attrs = {
            "attribution": ATTRIBUTION,
            "id": pod.id,
            "integration": DOMAIN,
            "suggested_area": "Outside",
            "total_kwh": pod.total_kwh,
            "total_kwh_difference": self.total_kwh_diff,
            "current_kwh": pod.current_kwh,
        }

        self.extra_attrs = attrs

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        return self.extra_attrs

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
    def state_class(self) -> str:
        return STATE_CLASS_TOTAL

    @property
    def last_reset(self) -> datetime:
        if len(self.pod.charges) <= 0:
            return datetime.now(tz=timezone.utc)

        # Get the most recent charge
        charge = self.pod.charges[0]
        return charge.starts_at - timedelta(seconds=10)

    @property
    def icon(self):
        icon = "mdi:car"

        if self.connected:
            icon = "mdi:car-electric"

        return icon

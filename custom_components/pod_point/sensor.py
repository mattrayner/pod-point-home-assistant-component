"""Sensor platform for pod_point."""
import logging
from typing import Dict, Any
from datetime import datetime, timedelta, timezone

from podpointclient.pod import Pod

from homeassistant.components.sensor import (
    STATE_CLASS_TOTAL,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ENERGY_KILO_WATT_HOUR,
    DEVICE_CLASS_ENERGY,
)
from homeassistant.core import callback

from .const import ATTR_STATE, ATTRIBUTION, DOMAIN, ICON, ICON_1C, ICON_2C
from .entity import PodPointEntity
from .coordinator import PodPointDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator: PodPointDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    # Handle coordinator offline on boot - no data will be populated
    if coordinator.online is False:
        return

    sensors = []

    for i in range(len(coordinator.data)):
        pps = PodPointSensor(coordinator, entry, i)
        ppcts = PodPointChargeTimeSensor(coordinator, entry, i)
        pptes = PodPointTotalEnergySensor(coordinator, entry, i)
        ppces = PodPointCurrentEnergySensor(coordinator, entry, i)

        sensors.append(pps)
        sensors.append(ppcts)
        sensors.append(pptes)
        sensors.append(ppces)

    async_add_devices(sensors)


class PodPointSensor(
    PodPointEntity,
    SensorEntity,
):
    """pod_point Sensor class."""

    @property
    def device_class(self) -> str:
        return f"{DOMAIN}__pod"

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


class PodPointChargeTimeSensor(
    PodPointEntity,
    SensorEntity,
):
    """pod_point Sensor class."""

    @property
    def device_class(self) -> str:
        return f"{DOMAIN}__pod_charge_time"

    @property
    def unique_id(self):
        return f"{super().unique_id}_charge_time"

    @property
    def name(self) -> str:
        return f"{self.pod.ppid} Completed Charge Time"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return {
            "raw": self.pod.total_charge_seconds,
            "formatted": str(timedelta(seconds=self.pod.total_charge_seconds)),
            "long": self._td_format(timedelta(seconds=self.pod.total_charge_seconds)),
        }

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.extra_state_attributes["raw"]

    @property
    def native_unit_of_measurement(self):
        """Return the unit for this sensor."""
        return "seconds"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:timer"

    @property
    def entity_picture(self) -> str:
        return None

    @property
    def state_class(self) -> str:
        return STATE_CLASS_TOTAL_INCREASING


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
        """This sensor is on when the given pod is connected to a vehicle"""
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

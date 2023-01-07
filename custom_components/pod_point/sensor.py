"""Sensor platform for pod_point."""
import logging
from typing import Dict, Any
from datetime import datetime, timedelta, timezone

from podpointclient.pod import Pod

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
    UnitOfTime,
    UnitOfEnergy,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback

from .const import (
    ATTR_STATE,
    ATTR_STATE_AVAILABLE,
    ATTR_STATE_CHARGING,
    ATTR_STATE_CONNECTED_WAITING,
    ATTR_STATE_OUT_OF_SERVICE,
    ATTR_STATE_UNAVAILABLE,
    ATTR_STATE_WAITING,
    ATTRIBUTION,
    CONF_CURRENCY,
    DEFAULT_CURRENCY,
    DOMAIN,
    ICON,
    ICON_1C,
    ICON_2C,
)
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
        pptcs = PodPointTotalCostSensor(coordinator, entry, i)
        pplcccs = PodPointLastCompleteChargeCostSensor(coordinator, entry, i)

        sensors.append(pps)
        sensors.append(ppcts)
        sensors.append(pptes)
        sensors.append(ppces)
        sensors.append(pptcs)
        sensors.append(pplcccs)

    async_add_devices(sensors)


class PodPointSensor(
    PodPointEntity,
    SensorEntity,
):
    """pod_point Sensor class."""

    _attr_options = [
        ATTR_STATE_AVAILABLE,
        ATTR_STATE_UNAVAILABLE,
        ATTR_STATE_CHARGING,
        ATTR_STATE_OUT_OF_SERVICE,
        ATTR_STATE_WAITING,
        ATTR_STATE_CONNECTED_WAITING,
    ]
    _attr_translation_key = "status"
    _attr_has_entity_name = True
    _attr_name = "Status"
    _attr_device_class = SensorDeviceClass.ENUM

    @property
    def unique_id(self):
        return f"{super().unique_id}_status"

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

    _attr_has_entity_name = True
    _attr_name = "Completed Charge Time"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_icon = "mdi:timer"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def unique_id(self):
        return f"{super().unique_id}_charge_time"

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
    def entity_picture(self) -> str:
        return None


class PodPointTotalEnergySensor(PodPointSensor):
    """pod_point total energy Sensor class."""

    _attr_options = None  # Override the options from PodPointSensor (prevents an error as this sensor is an 'energy' type)
    _attr_translation_key = None
    _attr_has_entity_name = True
    _attr_name = "Total Energy"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

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
    def native_value(self) -> float:
        return self.pod.total_kwh

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

    _attr_has_entity_name = True
    _attr_name = "Current Energy"
    _attr_state_class = SensorStateClass.TOTAL

    @property
    def unique_id(self):
        return f"{super().unique_id}_current_charge_energy"

    @property
    def native_value(self) -> float:
        return self.pod.current_kwh

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


class PodPointTotalCostSensor(
    PodPointEntity,
    SensorEntity,
):
    """pod_point total cost sensor class."""

    _attr_has_entity_name = True
    _attr_name = "Total Cost"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_icon = "mdi:cash-multiple"

    @property
    def unique_id(self):
        return f"{super().unique_id}_total_cost"

    @property
    def currency(self) -> str:
        """Which currency type are we returning?"""

        # TODO - Should we use the default currency from HA here? Seems weird to specify a aeperate value here...
        try:
            currency = self.config_entry.options[CONF_CURRENCY]
        except KeyError:
            currency = DEFAULT_CURRENCY

        return currency

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        cost_as_pounds = self.pod.total_cost / 100

        return {
            "raw": self.pod.total_cost,
            "amount": cost_as_pounds,
            "currency": self.currency,
            "formatted": f"{cost_as_pounds} {self.currency}",
        }

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.extra_state_attributes["amount"]

    @property
    def native_unit_of_measurement(self):
        """Return the unit for this sensor."""
        return self.extra_state_attributes["currency"]

    @property
    def entity_picture(self) -> str:
        return None


class PodPointLastCompleteChargeCostSensor(
    PodPointEntity,
    SensorEntity,
):
    """pod_point cost of last complete charge sensor class."""

    _attr_has_entity_name = True
    _attr_name = "Last Completed Charge Cost"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_icon = "mdi:cash"

    @property
    def unique_id(self):
        return f"{super().unique_id}_last_complete_charge_cost"

    @property
    def currency(self) -> str:
        """Which currency type are we returning?"""

        try:
            currency = self.config_entry.options[CONF_CURRENCY]
        except KeyError:
            currency = DEFAULT_CURRENCY

        return currency

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        raw = 0
        cost_as_pounds = 0.0

        if getattr(self.pod, "last_charge_cost", None) is not None:
            raw = getattr(self.pod, "last_charge_cost", None)
            cost_as_pounds = raw / 100

        return {
            "raw": raw,
            "amount": cost_as_pounds,
            "currency": self.currency,
            "formatted": f"{cost_as_pounds} {self.currency}",
        }

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.extra_state_attributes["amount"]

    @property
    def native_unit_of_measurement(self):
        """Return the unit for this sensor."""
        return self.extra_state_attributes["currency"]

    @property
    def entity_picture(self) -> str:
        return None

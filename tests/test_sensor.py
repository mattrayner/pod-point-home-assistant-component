"""Test pod_point switch."""
import asyncio

import aiohttp
import homeassistant.helpers.aiohttp_client as client
from .fixtures import POD_COMPLETE_FIXTURE
from unittest.mock import call, patch
from typing import List
from datetime import datetime

from homeassistant.components import switch
from homeassistant.components.switch import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.const import ATTR_ENTITY_ID
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.pod_point import async_setup_entry
from custom_components.pod_point.const import (
    CONF_CURRENCY,
    DEFAULT_NAME,
    DOMAIN,
    SENSOR,
    SWITCH,
    ATTR_STATE,
)
from custom_components.pod_point.sensor import (
    PodPointSensor,
    PodPointTotalEnergySensor,
    async_setup_entry,
)

from homeassistant.const import (
    ENERGY_KILO_WATT_HOUR,
    DEVICE_CLASS_ENERGY,
)

from homeassistant.components.sensor import (
    STATE_CLASS_TOTAL,
    STATE_CLASS_TOTAL_INCREASING,
)

from podpointclient.pod import Pod
from .test_coordinator import subject_with_data as coordinator_with_data

from .const import MOCK_CONFIG

from unittest.mock import Mock


async def setup_sensors(hass) -> List[PodPointSensor]:
    """Setup sensors within the test environment"""
    coordinator = await coordinator_with_data(hass)

    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    mock = Mock()

    await async_setup_entry(hass, config_entry, mock)

    print(mock.call_args_list)
    sensors: List[PodPointSensor] = mock.call_args_list[0][0][0]

    return (config_entry, sensors)


async def test_sensor_creation(hass, bypass_get_data):
    """Test that the expected number of sensors is created"""

    (_, sensors) = await setup_sensors(hass)

    assert 6 == len(sensors)


async def test_status_pod_sensor(hass, bypass_get_data):
    """Tests for pod status sensor."""
    (_, sensors) = await setup_sensors(hass)

    [status, _, _, _, _, _] = sensors

    assert "pod_point__pod" == status.device_class
    assert "pod_point_12234_PSL-123456_status" == status.unique_id
    assert "PSL-123456 Status" == status.name
    assert "charging" == status.native_value

    assert "mdi:ev-plug-type2" == status.icon
    assert "/api/pod_point/static/uc-03.png" == status.entity_picture

    status.pod.model.name = "XX-UC-XX-XX"
    assert "mdi:ev-plug-type2" == status.icon
    assert "/api/pod_point/static/uc.png" == status.entity_picture

    status.pod.model.name = "XX-2C-XX-XX"
    assert "mdi:ev-plug-type2" == status.icon
    assert "/api/pod_point/static/2c.png" == status.entity_picture

    status.pod.model.name = "XX-1C-XX-XX"
    assert "mdi:ev-plug-type1" == status.icon
    assert "/api/pod_point/static/2c.png" == status.entity_picture

    status.pod.model.name = "XX-XX-XX-XX"
    assert "mdi:ev-plug-type2" == status.icon
    assert "/api/pod_point/static/xx.png" == status.entity_picture


async def test_total_energy_pod_sensor(hass, bypass_get_data):
    """Tests for pod total eergy sensor."""
    (_, sensors) = await setup_sensors(hass)

    total_energy: PodPointTotalEnergySensor
    [_, _, total_energy, _, _, _] = sensors

    total_energy.async_write_ha_state = Mock()
    total_energy._handle_coordinator_update()
    assert {
        "attribution": "Data provided by https://pod-point.com/",
        "current_kwh": 0.0,
        "id": 12234,
        "integration": "pod_point",
        "suggested_area": "Outside",
        "total_kwh": 0.0,
        "total_kwh_difference": 0.0,
    } == total_energy.extra_attrs

    assert "pod_point_12234_PSL-123456_status_total_energy" == total_energy.unique_id

    assert "PSL-123456 Total Energy" == total_energy.name

    assert DEVICE_CLASS_ENERGY == total_energy.device_class
    assert STATE_CLASS_TOTAL_INCREASING == total_energy.state_class
    assert 0.0 == total_energy.native_value
    assert ENERGY_KILO_WATT_HOUR == total_energy.native_unit_of_measurement
    assert "mdi:lightning-bolt-outline" == total_energy.icon
    assert False == total_energy.is_on

    total_energy.extra_attrs[ATTR_STATE] = "charging"
    assert "mdi:lightning-bolt" == total_energy.icon
    assert True == total_energy.is_on


async def test_current_energy_pod_sensor(hass, bypass_get_data):
    """Tests for pod current energy sensor."""
    (_, sensors) = await setup_sensors(hass)

    [_, _, _, current_energy, _, _] = sensors

    assert (
        "pod_point_12234_PSL-123456_status_total_energy_current_charge_energy"
        == current_energy.unique_id
    )

    assert "PSL-123456 Current Energy" == current_energy.name

    assert DEVICE_CLASS_ENERGY == current_energy.device_class
    assert STATE_CLASS_TOTAL == current_energy.state_class
    assert 0.0 == current_energy.native_value
    assert "mdi:car-electric" == current_energy.icon

    current_energy.extra_state_attributes[ATTR_STATE] = "foo"
    assert "mdi:car" == current_energy.icon


async def test_total_charge_time_pod_sensor(hass, bypass_get_data):
    """Tests for pod total charge time sensor."""
    (_, sensors) = await setup_sensors(hass)

    [_, charge_time, _, _, _, _] = sensors

    assert "pod_point_12234_PSL-123456_charge_time" == charge_time.unique_id

    assert "PSL-123456 Completed Charge Time" == charge_time.name

    assert "pod_point__pod_charge_time" == charge_time.device_class
    assert 0 == charge_time.native_value
    assert {
        "formatted": "0:00:00",
        "long": "0s",
        "raw": 0,
    } == charge_time.extra_state_attributes
    assert "mdi:timer" == charge_time.icon

    charge_time.pod.total_charge_seconds = 61
    assert 61 == charge_time.native_value
    assert {
        "formatted": "0:01:01",
        "long": "1 minute",
        "raw": 61,
    } == charge_time.extra_state_attributes

    charge_time.pod.total_charge_seconds = 9945
    assert 9945 == charge_time.native_value
    assert {
        "formatted": "2:45:45",
        "long": "2 hours, 45 minutes, 45 seconds",
        "raw": 9945,
    } == charge_time.extra_state_attributes

    charge_time.pod.total_charge_seconds = 175545
    assert 175545 == charge_time.native_value
    assert {
        "formatted": "2 days, 0:45:45",
        "long": "2 days, 45 minutes, 45 seconds",
        "raw": 175545,
    } == charge_time.extra_state_attributes

    charge_time.pod.total_charge_seconds = 2764800
    assert 2764800 == charge_time.native_value
    assert {
        "formatted": "32 days, 0:00:00",
        "long": "1 month, 2 days",
        "raw": 2764800,
    } == charge_time.extra_state_attributes

    charge_time.pod.total_charge_seconds = 66355200
    assert 66355200 == charge_time.native_value
    assert {
        "formatted": "768 days, 0:00:00",
        "long": "2 years, 1 month, 8 days",
        "raw": 66355200,
    } == charge_time.extra_state_attributes


async def test_total_cost_pod_sensor(hass, bypass_get_data):
    """Tests for pod total charge time sensor."""
    (_, sensors) = await setup_sensors(hass)

    [_, _, _, _, total_cost, _] = sensors

    assert "pod_point_12234_PSL-123456_total_cost" == total_cost.unique_id

    assert "PSL-123456 Total Cost" == total_cost.name

    assert "monetary" == total_cost.device_class
    assert 0 == total_cost.native_value
    assert {
        "amount": 0.0,
        "currency": "GBP",
        "formatted": "0.0 GBP",
        "raw": 0,
    } == total_cost.extra_state_attributes
    assert "mdi:cash-multiple" == total_cost.icon

    total_cost.pod.total_cost = 61
    assert 0.61 == total_cost.native_value
    assert {
        "amount": 0.61,
        "currency": "GBP",
        "formatted": "0.61 GBP",
        "raw": 61,
    } == total_cost.extra_state_attributes

    total_cost.pod.total_cost = 9945
    assert 99.45 == total_cost.native_value
    assert {
        "amount": 99.45,
        "currency": "GBP",
        "formatted": "99.45 GBP",
        "raw": 9945,
    } == total_cost.extra_state_attributes

    total_cost.pod.total_cost = 175545
    assert 1755.45 == total_cost.native_value
    assert {
        "amount": 1755.45,
        "currency": "GBP",
        "formatted": "1755.45 GBP",
        "raw": 175545,
    } == total_cost.extra_state_attributes

    total_cost.pod.total_cost = 2764800
    assert 27648.00 == total_cost.native_value
    assert {
        "amount": 27648.0,
        "currency": "GBP",
        "formatted": "27648.0 GBP",
        "raw": 2764800,
    } == total_cost.extra_state_attributes

    assert total_cost.currency == "GBP"


async def test_last_charge_cost_pod_sensor(hass, bypass_get_data):
    """Tests for pod total charge time sensor."""
    (_, sensors) = await setup_sensors(hass)

    [_, _, _, _, _, last_charge] = sensors

    assert (
        "pod_point_12234_PSL-123456_last_complete_charge_cost" == last_charge.unique_id
    )

    assert "PSL-123456 Last Complete Charge Cost" == last_charge.name

    assert "monetary" == last_charge.device_class
    assert 0 == last_charge.native_value
    assert {
        "amount": 0.0,
        "currency": "GBP",
        "formatted": "0.0 GBP",
        "raw": 0,
    } == last_charge.extra_state_attributes
    assert "mdi:cash" == last_charge.icon

    assert 0.0 == last_charge.native_value
    assert {
        "amount": 0.0,
        "currency": "GBP",
        "formatted": "0.0 GBP",
        "raw": 0,
    } == last_charge.extra_state_attributes

    setattr(last_charge.pod, "last_charge_cost", 9945)
    assert 99.45 == last_charge.native_value
    assert {
        "amount": 99.45,
        "currency": "GBP",
        "formatted": "99.45 GBP",
        "raw": 9945,
    } == last_charge.extra_state_attributes

    assert last_charge.currency == "GBP"

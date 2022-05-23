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
from custom_components.pod_point.const import DEFAULT_NAME, DOMAIN, SENSOR, SWITCH, ATTR_STATE
from custom_components.pod_point.sensor import PodPointSensor, PodPointTotalEnergySensor, async_setup_entry

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
    sensors: List[PodPointSensor] =  mock.call_args_list[0][0][0]

    return (config_entry, sensors)

async def test_sensor_creation(hass, bypass_get_data):
    """Test that the expected number of sensors is created"""

    (_, sensors) = await setup_sensors(hass)

    assert 3 == len(sensors)


async def test_status_pod_sensor(hass, bypass_get_data):
    """Tests for pod status sensor."""
    (_, sensors) = await setup_sensors(hass)

    assert 3 == len(sensors)

    [status, _, _] = sensors

    assert "pod_point__pod"                     == status.device_class
    assert "pod_point_12234_PSL-123456_status"  == status.unique_id
    assert "PSL-123456 Status"                  == status.name
    assert "charging"                           == status.native_value

    assert "mdi:ev-plug-type2"                  == status.icon
    assert "/api/pod_point/static/uc-03.png"    == status.entity_picture

    status.pod.model.name                   = "XX-UC-XX-XX"
    assert "mdi:ev-plug-type2"              == status.icon
    assert "/api/pod_point/static/uc.png"   == status.entity_picture

    status.pod.model.name                   = "XX-2C-XX-XX"
    assert "mdi:ev-plug-type2"              == status.icon
    assert "/api/pod_point/static/2c.png"   == status.entity_picture

    status.pod.model.name                   = "XX-1C-XX-XX"
    assert "mdi:ev-plug-type1"              == status.icon
    assert "/api/pod_point/static/2c.png"   == status.entity_picture

    status.pod.model.name                   = "XX-XX-XX-XX"
    assert "mdi:ev-plug-type2"              == status.icon
    assert "/api/pod_point/static/xx.png"   == status.entity_picture

async def test_total_energy_pod_sensor(hass, bypass_get_data):
    """Tests for pod total eergy sensor."""
    (_, sensors) = await setup_sensors(hass)

    assert 3 == len(sensors)

    total_energy: PodPointTotalEnergySensor
    [_, total_energy, _] = sensors

    total_energy.async_write_ha_state = Mock()
    total_energy._handle_coordinator_update()
    assert {
        'attribution': 'Data provided by https://pod-point.com/',
        'current_kwh': 0.0,
        'id': 12234,
        'integration': 'pod_point',
        'suggested_area': 'Outside',
        'total_kwh': 0.0,
        'total_kwh_difference': 0.0
    } == total_energy.extra_attrs

    assert "pod_point_12234_PSL-123456_status_total_energy" == total_energy.unique_id 

    assert "PSL-123456 Total Energy" == total_energy.name 

    assert DEVICE_CLASS_ENERGY          == total_energy.device_class 
    assert STATE_CLASS_TOTAL_INCREASING == total_energy.state_class 
    assert 0.0                          == total_energy.native_value
    assert ENERGY_KILO_WATT_HOUR        == total_energy.native_unit_of_measurement
    assert "mdi:lightning-bolt-outline" == total_energy.icon
    assert False                        == total_energy.is_on

    total_energy.extra_attrs[ATTR_STATE]    = "charging"
    assert "mdi:lightning-bolt"             == total_energy.icon
    assert True                             == total_energy.is_on

async def test_current_energy_pod_sensor(hass, bypass_get_data):
    """Tests for pod current energy sensor."""
    (_, sensors) = await setup_sensors(hass)

    [_, _, current_energy] = sensors

    assert "pod_point_12234_PSL-123456_status_total_energy_current_charge_energy" == current_energy.unique_id 

    assert "PSL-123456 Current Energy" == current_energy.name 

    assert DEVICE_CLASS_ENERGY  == current_energy.device_class 
    assert STATE_CLASS_TOTAL    == current_energy.state_class 
    assert 0.0                  == current_energy.native_value
    assert "mdi:car-electric"   == current_energy.icon

    current_energy.extra_state_attributes[ATTR_STATE]   = "foo"
    assert "mdi:car"                                    == current_energy.icon

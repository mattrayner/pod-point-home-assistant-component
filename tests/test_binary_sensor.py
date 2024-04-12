"""Test pod_point binary sensors."""

from typing import List, Union
from unittest.mock import Mock, call, patch

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.entity import EntityCategory
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.pod_point import async_setup_entry
from custom_components.pod_point.const import (
    ATTR_CONNECTION_STATE_ONLINE,
    DOMAIN, ATTR_STATE,
)
from custom_components.pod_point.binary_sensor import (
    PodPointCableConnectionSensor,
    PodPointCloudConnectionSensor,
    async_setup_entry,
)
from podpointclient.connectivity_status import ConnectivityStatus, Evse

from .const import MOCK_CONFIG
from .fixtures import CONNECTIVITY_STATUS_COMPLETE_FIXTURE
from .test_coordinator import subject_with_data as coordinator_with_data


async def setup_sensors(hass) -> List[BinarySensorEntity]:
    """Setup sensors within the test environment"""
    coordinator = await coordinator_with_data(hass)

    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    mock = Mock()

    await async_setup_entry(hass, config_entry, mock)

    print(mock.call_args_list)
    sensors: List[Union(PodPointCableConnectionSensor, PodPointCloudConnectionSensor)] = (
        mock.call_args_list[0][0][0]
    )

    return (config_entry, sensors)


@pytest.mark.asyncio
async def test_sensor_creation(hass, bypass_get_data):
    """Test that the expected number of sensors is created"""

    (_, sensors) = await setup_sensors(hass)

    assert 2 == len(sensors)


@pytest.mark.asyncio
async def test_cloud_connection_sensor(hass, bypass_get_data):
    """Tests for pod status sensor."""
    (_, sensors) = await setup_sensors(hass)

    [_, status] = sensors

    assert BinarySensorDeviceClass.CONNECTIVITY == status.device_class
    assert EntityCategory.DIAGNOSTIC == status.entity_category
    assert "pod_point_12234_PSL-123456_cloud_connection" == status.unique_id
    assert "Cloud Connection" == status.name

    status.pod.connectivity_status = ConnectivityStatus(CONNECTIVITY_STATUS_COMPLETE_FIXTURE)
    assert status.is_on is True
    assert "mdi:cloud-check-variant" == status.icon

    status.pod.connectivity_status.evses[0].connectivity_state.connectivity_status = "FOO"
    assert status.is_on is False
    assert "mdi:cloud-off" == status.icon


@pytest.mark.asyncio
async def test_cable_connection_sensor(hass, bypass_get_data):
    """Tests for pod status sensor."""
    (_, sensors) = await setup_sensors(hass)

    [status, _] = sensors

    assert BinarySensorDeviceClass.PLUG == status.device_class
    assert "pod_point_12234_PSL-123456_cable_status" == status.unique_id
    assert "Cable Status" == status.name

    status.extra_attrs[ATTR_STATE] = "charging"
    assert status.is_on is True

    status.extra_attrs[ATTR_STATE] = "available"
    assert status.is_on is False

    status.extra_attrs[ATTR_STATE] = "connected-waiting-for-schedule"
    assert status.is_on is True

    status.extra_attrs[ATTR_STATE] = "suspended-evse"
    assert status.is_on is True

    status.extra_attrs[ATTR_STATE] = "suspended-ev"
    assert status.is_on is True

    status.extra_attrs[ATTR_STATE] = "foo"
    assert status.is_on is False


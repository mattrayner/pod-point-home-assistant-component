"""Test pod_point sensors."""

import asyncio
import pytest
import aiohttp
import homeassistant.helpers.aiohttp_client as client
from homeassistant.components.sensor import SensorDeviceClass
from .fixtures import POD_COMPLETE_FIXTURE
from unittest.mock import call, patch
from typing import List, Union
from datetime import datetime

from homeassistant.components import switch
from homeassistant.components.switch import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.const import ATTR_ENTITY_ID
from pytest_homeassistant_custom_component.common import MockConfigEntry

# from custom_components.pod_point import async_setup_entry
from custom_components.pod_point.const import (
    CONF_CURRENCY,
    DEFAULT_NAME,
    DOMAIN,
    SENSOR,
    SWITCH,
    ATTR_STATE,
    ATTR_STATE_AVAILABLE,
    ATTR_STATE_UNAVAILABLE,
    ATTR_STATE_CHARGING,
    ATTR_STATE_OUT_OF_SERVICE,
    ATTR_STATE_WAITING,
    ATTR_STATE_CONNECTED_WAITING,
)
from custom_components.pod_point.update import (
    PodUpdateEntity,
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


async def setup_updates(hass) -> List[PodUpdateEntity]:
    """Setup updates within the test environment"""
    coordinator = await coordinator_with_data(hass)

    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    mock = Mock()

    await async_setup_entry(hass, config_entry, mock)

    print(mock.call_args_list)
    updates: List[PodUpdateEntity] = mock.call_args_list[0][0][0]

    return (config_entry, updates)


@pytest.mark.asyncio
async def test_update_sensor(hass, bypass_get_data):
    """Tests for pod updates sensor."""
    (_, updates) = await setup_updates(hass)

    [update] = updates

    assert "pod_point_12234_PSL-123456_update" == update.unique_id

    assert "A30P-3.1.22-00001" == update.installed_version
    assert "A30P-3.1.22-00001" == update.latest_version
    assert "PSL-123456 is up to date!" == update.release_notes()

    update.pod.firmware.update_status.is_update_available = True
    assert "A30P-3.1.22-00001_UPDATE_AVAILABLE" == update.latest_version
    assert (
        "A firmware update is available for PSL-123456.\n\nExternal updating is not supported by the PodPoint APIs, please check the PodPoint mobile app for next steps."
        == update.release_notes()
    )

"""Test pod_point switch."""
import asyncio

import aiohttp
import homeassistant.helpers.aiohttp_client as client
from .fixtures import POD_COMPLETE_FIXTURE
from unittest.mock import call, patch

from homeassistant.components import switch
from homeassistant.components.switch import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.const import ATTR_ENTITY_ID
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.pod_point import async_setup_entry
from custom_components.pod_point.const import DEFAULT_NAME, DOMAIN, SWITCH

from podpointclient.pod import Pod

from .const import MOCK_CONFIG


async def test_switch_services(hass, bypass_get_data):
    """Test switch services."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    # Functions/objects can be patched directly in test code as well and can be used to test
    # additional things, like whether a function was called or what arguments it was called with
    with patch("podpointclient.client.PodPointClient.async_set_schedule") as title_func:
        await hass.services.async_call(
            SWITCH,
            SERVICE_TURN_OFF,
            service_data={ATTR_ENTITY_ID: "switch.psl_123456_charging_allowed"},
            blocking=True,
        )
        assert title_func.called

        flag = title_func.call_args.kwargs["enabled"]
        pod_type = type(title_func.call_args.kwargs["pod"])
        assert True == flag
        assert Pod == pod_type

        title_func.reset_mock()

        await hass.services.async_call(
            SWITCH,
            SERVICE_TURN_ON,
            service_data={ATTR_ENTITY_ID: "switch.psl_123456_charging_allowed"},
            blocking=True,
        )
        assert title_func.called

        flag = title_func.call_args.kwargs["enabled"]
        pod_type = type(title_func.call_args.kwargs["pod"])
        assert False == flag
        assert Pod == pod_type

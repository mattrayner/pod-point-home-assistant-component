"""Test pod_point switch."""

from unittest.mock import patch

from homeassistant.components.switch import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.const import ATTR_ENTITY_ID
from podpointclient.pod import Pod
from time import sleep
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.pod_point import async_setup_entry
from custom_components.pod_point.const import DOMAIN, SWITCH

from .const import MOCK_CONFIG


@pytest.mark.asyncio
@pytest.mark.enable_socket
async def test_allow_charging_switch(hass, bypass_get_data):
    """Test allow charging switch"""
    # Create a mock entry so we don't have to go through config flow
    print("CREATE CONFIG ENTRY")
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    print("---> SETUP CONFIG ENTRY")
    assert await async_setup_entry(hass, config_entry)
    print("---> WAIT")
    waited = await hass.async_block_till_done()
    print(f"---> WAITED {waited}")

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


@pytest.mark.asyncio
@pytest.mark.enable_socket
async def test_charge_mode_switch(hass, bypass_get_data):
    """Test charge mode switch"""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    # Functions/objects can be patched directly in test code as well and can be used to test
    # additional things, like whether a function was called or what arguments it was called with
    with patch(
        "podpointclient.client.PodPointClient.async_set_charge_mode_smart"
    ) as smart_mode_func:
        await hass.services.async_call(
            SWITCH,
            SERVICE_TURN_ON,
            service_data={ATTR_ENTITY_ID: "switch.psl_123456_smart_charge_mode"},
            blocking=True,
        )
        assert smart_mode_func.called

        pod_type = type(smart_mode_func.call_args.args[0])
        assert Pod == pod_type

    with patch(
        "podpointclient.client.PodPointClient.async_set_charge_mode_manual"
    ) as manual_mode_func:
        await hass.services.async_call(
            SWITCH,
            SERVICE_TURN_OFF,
            service_data={ATTR_ENTITY_ID: "switch.psl_123456_smart_charge_mode"},
            blocking=True,
        )
        assert manual_mode_func.called

        pod_type = type(manual_mode_func.call_args.args[0])
        assert Pod == pod_type

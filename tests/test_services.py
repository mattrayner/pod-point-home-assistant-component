"""Test pod_point services."""

from unittest.mock import patch

from podpointclient.pod import Pod
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.pod_point.const import DOMAIN, SERVICE_CHARGE_NOW
from custom_components.pod_point.services import PodPointServiceException

from .const import MOCK_CONFIG


@pytest.mark.asyncio
@pytest.mark.enable_socket
async def test_charge_now_service_with_data(hass, bypass_get_data):
    """Test charge_mode service"""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Functions/objects can be patched directly in test code as well and can be used to test
    # additional things, like whether a function was called or what arguments it was called with
    with patch(
        "podpointclient.client.PodPointClient.async_set_charge_override"
    ) as title_func:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_CHARGE_NOW,
            {
                "config_entry_id": "test",
                "hours": 3,
                "minutes": 2,
                "seconds": 1,
            },
            blocking=True,
        )
        assert title_func.called

        pod_type = type(title_func.call_args.kwargs["pod"])
        hours = title_func.call_args.kwargs["hours"]
        minutes = title_func.call_args.kwargs["minutes"]
        seconds = title_func.call_args.kwargs["seconds"]
        assert Pod == pod_type
        assert 3 == hours
        assert 2 == minutes
        assert 1 == seconds

        title_func.reset_mock()

        await hass.services.async_call(
            DOMAIN,
            SERVICE_CHARGE_NOW,
            {
                "config_entry_id": "test",
                "seconds": 1,
            },
            blocking=True,
        )
        assert title_func.called

        pod_type = type(title_func.call_args.kwargs["pod"])
        hours = title_func.call_args.kwargs["hours"]
        minutes = title_func.call_args.kwargs["minutes"]
        seconds = title_func.call_args.kwargs["seconds"]
        assert Pod == pod_type
        assert 0 == hours
        assert 0 == minutes
        assert 1 == seconds

        title_func.reset_mock()

        with pytest.raises(PodPointServiceException):
            await hass.services.async_call(
                DOMAIN,
                SERVICE_CHARGE_NOW,
                {"config_entry_id": "test"},
                blocking=True,
            )

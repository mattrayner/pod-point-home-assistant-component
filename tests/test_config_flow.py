"""Test pod_point config flow."""

from types import MappingProxyType
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info import dhcp
from homeassistant.core import HomeAssistant
import pytest
from podpointclient.errors import MfaInvalidCode, MfaRequired
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.pod_point.const import (
    BINARY_SENSOR,
    CONF_CURRENCY,
    CONF_HTTP_DEBUG,
    CONF_PASSWORD,
    CONF_REFRESH_TOKEN,
    CONF_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
    SENSOR,
    SWITCH,
    UPDATE,
)

from .const import MOCK_CONFIG

DHCP_SERVICE_INFO = dhcp.DhcpServiceInfo(
    hostname="podpoint-245EBE000000",
    ip="192.168.1.200",
    macaddress="245EBE000000",
)


# This fixture bypasses the actual setup of the integration
# since we only want to test the config flow. We test the
# actual functionality of the integration in other test modules.
@pytest.fixture(autouse=True)
def bypass_setup_fixture():
    """Prevent setup."""
    with patch(
        "custom_components.pod_point.async_setup",
        return_value=True,
    ), patch(
        "custom_components.pod_point.async_setup_entry",
        return_value=True,
    ):
        yield


# Here we simiulate a successful config flow from the backend.
# Note that we use the `bypass_get_data` fixture here because
# we want the config flow validation to succeed during the test.
@pytest.mark.asyncio
async def test_successful_config_flow(hass, bypass_get_data):
    """Test a successful config flow."""
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # If a user were to enter `test_username` for username and `test_password`
    # for password, it would result in this function call
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_CONFIG
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "test@example.com"
    assert result["data"] == MOCK_CONFIG
    assert result["result"]


# Here we simiulate a successful reauth config flow from the backend.
# Note that we use the `bypass_get_data` fixture here because
# we want the config flow validation to succeed during the test.
@pytest.mark.asyncio
async def test_reauth_config_flow(hass, bypass_get_data):
    """Test a successful config flow."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    entry.add_to_hass(hass)

    # Initialize a config flow
    entry.async_start_reauth(hass)
    await hass.async_block_till_done()
    flows = hass.config_entries.flow.async_progress()
    assert len(flows) == 1
    result = flows[0]

    # Check that the config flow shows the reauth form as the first step
    # assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

    # If a user were to confirm the re-auth start, this function call
    result_2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )

    # It should load the user form
    assert result_2["type"] == FlowResultType.FORM
    assert result_2["step_id"] == "user"

    updated_config = {**MOCK_CONFIG, CONF_PASSWORD: "NewH8x0rP455!"}

    # If a user entered a new password, this would happen
    result_3 = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=updated_config
    )

    # Reauthentication updates the existing entry.
    assert result_3["type"] == FlowResultType.ABORT
    assert result_3["reason"] == "reauth_successful"
    assert entry.data == updated_config


# In this case, we want to simulate a failure during the config flow.
# We use the `error_on_get_data` mock instead of `bypass_get_data`
# (note the function parameters) to raise an Exception during
# validation of the input config.
@pytest.mark.asyncio
async def test_failed_config_flow(hass, error_on_get_data):
    """Test a failed config flow due to credential validation failure."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_CONFIG
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "auth"}


# Our config flow also has an options flow, so we must test it as well.
@pytest.mark.asyncio
async def test_options_flow(hass, bypass_get_data):
    """Test an options flow."""
    # Create a new MockConfigEntry and add to HASS (we're bypassing config
    # flow entirely)
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    entry.add_to_hass(hass)

    # Initialize an options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)

    # Verify that the first options step is a user form
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # Enter some fake data into the form
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={platform: platform != SENSOR for platform in PLATFORMS},
    )

    # Verify that the flow finishes
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "test@example.com"

    # Verify that the options were updated
    assert entry.options == MappingProxyType(
        {
            BINARY_SENSOR: True,
            SENSOR: False,
            SWITCH: True,
            UPDATE: True,
            CONF_SCAN_INTERVAL: 300,
            CONF_HTTP_DEBUG: False,
            CONF_CURRENCY: "GBP",
        }
    )


# Our config flow also has an DHCP flow, so we must test it as well.
@pytest.mark.asyncio
async def test_dhcp_flow(hass: HomeAssistant, bypass_get_data) -> None:
    """Test that DHCP discovery works."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        data=DHCP_SERVICE_INFO,
        context={"source": config_entries.SOURCE_DHCP},
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_CONFIG
    )

    assert result2["type"] == "create_entry"
    assert result2["data"] == MOCK_CONFIG


@pytest.mark.asyncio
async def test_dhcp_login_error(hass: HomeAssistant, bypass_get_data) -> None:
    """Test DHCP login error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        data=DHCP_SERVICE_INFO,
        context={"source": config_entries.SOURCE_DHCP},
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    with patch(
        "podpointclient.client.PodPointClient.async_credentials_verified",
        return_value=False,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            MOCK_CONFIG,
        )
        assert result["errors"] == {"base": "auth"}


@pytest.mark.parametrize("reauth", [False, True])
async def test_sms_config_flow(hass, reauth):
    """Request an SMS, allow a retry, and save only the refresh token."""
    if reauth:
        entry = MockConfigEntry(
            domain=DOMAIN, data={**MOCK_CONFIG, CONF_REFRESH_TOKEN: "old-token"}
        )
        entry.add_to_hass(hass)
        entry.async_start_reauth(hass)
        await hass.async_block_till_done()
        flow = hass.config_entries.flow.async_progress()[0]
        flow = await hass.config_entries.flow.async_configure(flow["flow_id"], {})
    else:
        flow = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

    client = MagicMock()
    client.email = MOCK_CONFIG["email"]
    client.password = MOCK_CONFIG[CONF_PASSWORD]
    client.async_credentials_verified = AsyncMock(side_effect=[MfaRequired(), True])
    client.auth.async_start_mfa = AsyncMock()
    client.auth.async_complete_mfa = AsyncMock(
        side_effect=[MfaInvalidCode(400, "Incorrect code"), True]
    )
    client.auth.refresh_token = "new-token"

    with patch("custom_components.pod_point.config_flow.PodPointClient", return_value=client):
        flow = await hass.config_entries.flow.async_configure(flow["flow_id"], MOCK_CONFIG)
        assert flow["step_id"] == "mfa"
        client.auth.async_start_mfa.assert_awaited_once()

        flow = await hass.config_entries.flow.async_configure(flow["flow_id"], {"code": "000000"})
        assert flow["errors"] == {"base": "mfa_code"}

        flow = await hass.config_entries.flow.async_configure(flow["flow_id"], {"code": "012345"})
        client.auth.async_complete_mfa.assert_awaited_with("012345")

    expected = {**MOCK_CONFIG, CONF_REFRESH_TOKEN: "new-token"}
    if reauth:
        assert flow["reason"] == "reauth_successful"
        assert entry.data == expected
    else:
        assert flow["type"] == FlowResultType.CREATE_ENTRY
        assert flow["data"] == expected

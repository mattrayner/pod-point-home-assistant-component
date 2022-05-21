"""Test pod_point setup process."""
# from unittest import mock
from email.headerregistry import ContentTransferEncodingHeader
from unittest.mock import MagicMock
from homeassistant.exceptions import ConfigEntryNotReady
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.pod_point.coordinator import (
    PodPointDataUpdateCoordinator,
    UpdateFailed,
)
from custom_components.pod_point.const import DOMAIN
from custom_components.pod_point import async_setup_entry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.exceptions import ConfigEntryAuthFailed
from podpointclient.client import PodPointClient
from podpointclient.pod import Pod
from podpointclient.errors import AuthError, ApiConnectionError, SessionError
from podpointclient.factories import PodFactory

from .const import MOCK_CONFIG
from .fixtures import POD_COMPLETE_FIXTURE


async def subject(hass) -> PodPointDataUpdateCoordinator:
    """Rerturn a setup coordinator"""
    session = async_get_clientsession(hass)
    client = PodPointClient(
        username="test@example.com", password="password", session=session
    )

    # Setup our data coordinator with the desired scan interval
    return PodPointDataUpdateCoordinator(hass, client=client, scan_interval=300)


async def subject_with_data(hass) -> PodPointDataUpdateCoordinator:
    """Return a setup coodrinator with pods"""
    pod_factory = PodFactory()
    pods = pod_factory.build_pods({"pods": [POD_COMPLETE_FIXTURE]})

    coordinator: PodPointDataUpdateCoordinator = await subject(hass)
    coordinator.pods = pods
    coordinator.data = pods
    coordinator.online = True
    return coordinator


async def subject_with_data_offline(hass) -> PodPointDataUpdateCoordinator:
    """Return an offline marked coordinator"""
    coordinator: PodPointDataUpdateCoordinator = await subject_with_data(hass)
    coordinator.online = False

    return coordinator


# Test that refreshes work as expected and populate pods
async def test_coordinator_refresh(hass, bypass_get_data):
    """Test entry setup and unload."""
    coordinator: PodPointDataUpdateCoordinator = await subject(hass)
    assert coordinator.online == None

    coordinator.online = False

    await coordinator.async_refresh()

    assert len(coordinator.data) == 1
    assert coordinator.online is True

    pod = coordinator.data[0]
    assert isinstance(pod, Pod)
    assert len(pod.charges) == 9


# Test refreshes with connection errors fail as expected
async def test_coordinator_refresh_connection_error(hass, error_on_get_data):
    """Test entry setup and unload."""
    # coordinator: PodPointDataUpdateCoordinator = await subject_with_data(hass)

    session = async_get_clientsession(hass)
    client = PodPointClient(
        username="test@example.com", password="password", session=session
    )

    client.async_get_pods = MagicMock(
        side_effect=ApiConnectionError("CONNECTION_ERROR_MESSAGE")
    )

    # Setup our data coordinator with the desired scan interval
    coordinator = PodPointDataUpdateCoordinator(hass, client=client, scan_interval=300)

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

    assert coordinator.online is False


# Test refreshes with auth an session errrors fail as expected
async def test_coordinator_refresh_auth_session_error(hass, error_on_get_data):
    """Test entry setup and unload."""
    # coordinator: PodPointDataUpdateCoordinator = await subject_with_data(hass)

    session = async_get_clientsession(hass)
    client = PodPointClient(
        username="test@example.com", password="password", session=session
    )

    client.async_get_pods = MagicMock(side_effect=AuthError(401, "AUTH_ERROR_MESSAGE"))

    # Setup our data coordinator with the desired scan interval
    coordinator = PodPointDataUpdateCoordinator(hass, client=client, scan_interval=300)

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()

    client.async_get_pods = MagicMock(
        side_effect=SessionError(401, "AUTH_ERROR_MESSAGE")
    )

    # Setup our data coordinator with the desired scan interval
    coordinator = PodPointDataUpdateCoordinator(hass, client=client, scan_interval=300)

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()


# Test refreshes with an exception fail as expected
async def test_coordinator_refresh_unexpected_exception(hass, error_on_get_data):
    """Test entry setup and unload."""
    # coordinator: PodPointDataUpdateCoordinator = await subject_with_data(hass)

    session = async_get_clientsession(hass)
    client = PodPointClient(
        username="test@example.com", password="password", session=session
    )

    client.async_get_pods = MagicMock(side_effect=KeyError("CONNECTION_ERROR_MESSAGE"))

    # Setup our data coordinator with the desired scan interval
    coordinator = PodPointDataUpdateCoordinator(hass, client=client, scan_interval=300)

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

"""Test pod_point setup process."""

# from unittest import mock
from datetime import timedelta
from email.headerregistry import ContentTransferEncodingHeader
from unittest.mock import MagicMock

from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from podpointclient.client import PodPointClient
from podpointclient.errors import ApiConnectionError, AuthError, SessionError
from podpointclient.factories import FirmwareFactory, PodFactory, UserFactory
from podpointclient.pod import Pod
from podpointclient.user import User
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.pod_point import async_setup_entry
from custom_components.pod_point.const import DOMAIN
from custom_components.pod_point.coordinator import (
    PodPointDataUpdateCoordinator,
    UpdateFailed,
)

from .const import MOCK_CONFIG
from .fixtures import (
    FIRMWARE_COMPLETE_FIXTURE,
    POD_COMPLETE_FIXTURE,
    USER_COMPLETE_FIXTURE,
)


async def subject(hass) -> PodPointDataUpdateCoordinator:
    """Rerturn a setup coordinator"""
    session = async_get_clientsession(hass)
    client = PodPointClient(
        username="test@example.com", password="password", session=session
    )

    # Setup our data coordinator with the desired scan interval
    return PodPointDataUpdateCoordinator(
        hass, client=client, scan_interval=timedelta(seconds=3000)
    )


async def subject_with_data(hass) -> PodPointDataUpdateCoordinator:
    """Return a setup coodrinator with pods"""
    pod_factory = PodFactory()
    pods = pod_factory.build_pods({"pods": [POD_COMPLETE_FIXTURE]})
    firmware_factory = FirmwareFactory()
    pods[0].firmware = firmware_factory.build_firmwares(FIRMWARE_COMPLETE_FIXTURE)[0]
    user_factory = UserFactory()
    user = user_factory.build_user(USER_COMPLETE_FIXTURE)

    coordinator: PodPointDataUpdateCoordinator = await subject(hass)
    coordinator.pods = pods
    coordinator.data = pods
    coordinator.user = user
    coordinator.online = True
    return coordinator


async def subject_with_data_offline(hass) -> PodPointDataUpdateCoordinator:
    """Return an offline marked coordinator"""
    coordinator: PodPointDataUpdateCoordinator = await subject_with_data(hass)
    coordinator.online = False

    return coordinator


# Test that refreshes work as expected and populate pods
@pytest.mark.asyncio
async def test_coordinator_refresh(hass, bypass_get_data):
    """Test entry setup and unload."""
    coordinator: PodPointDataUpdateCoordinator = await subject(hass)
    assert coordinator.online is None

    coordinator.online = False

    await coordinator.async_refresh()

    assert len(coordinator.data) == 1
    assert coordinator.online is True

    pod = coordinator.data[0]
    assert isinstance(pod, Pod)
    assert len(pod.charges) == 9
    assert pod.last_charge_cost == 116
    assert isinstance(coordinator.user, User) is True


# Test refreshes with connection errors fail as expected
@pytest.mark.asyncio
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
    coordinator = PodPointDataUpdateCoordinator(
        hass, client=client, scan_interval=timedelta(seconds=300)
    )

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

    assert coordinator.online is False


# Test refreshes with auth an session errrors fail as expected
@pytest.mark.asyncio
async def test_coordinator_refresh_auth_session_error(hass, error_on_get_data):
    """Test entry setup and unload."""
    # coordinator: PodPointDataUpdateCoordinator = await subject_with_data(hass)

    session = async_get_clientsession(hass)
    client = PodPointClient(
        username="test@example.com", password="password", session=session
    )

    client.async_get_pods = MagicMock(side_effect=AuthError(401, "AUTH_ERROR_MESSAGE"))

    # Setup our data coordinator with the desired scan interval
    coordinator = PodPointDataUpdateCoordinator(
        hass, client=client, scan_interval=timedelta(seconds=300)
    )

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()

    client.async_get_pods = MagicMock(
        side_effect=SessionError(401, "AUTH_ERROR_MESSAGE")
    )

    # Setup our data coordinator with the desired scan interval
    coordinator = PodPointDataUpdateCoordinator(
        hass, client=client, scan_interval=timedelta(seconds=300)
    )

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()


# Test refreshes with an exception fail as expected
@pytest.mark.asyncio
async def test_coordinator_refresh_unexpected_exception(hass, error_on_get_data):
    """Test entry setup and unload."""
    # coordinator: PodPointDataUpdateCoordinator = await subject_with_data(hass)

    session = async_get_clientsession(hass)
    client = PodPointClient(
        username="test@example.com", password="password", session=session
    )

    client.async_get_pods = MagicMock(side_effect=KeyError("CONNECTION_ERROR_MESSAGE"))

    # Setup our data coordinator with the desired scan interval
    coordinator = PodPointDataUpdateCoordinator(
        hass, client=client, scan_interval=timedelta(seconds=300)
    )

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


# TODO: Add a test for repair flow creation and cleanup


# Pod Point can return a charge schedule with no status, in which case
# podpointclient leaves Schedule.status as None. Schedule.dict and
# Schedule.is_active both dereference it unconditionally, so one such schedule
# raised AttributeError and took down every platform at setup.
@pytest.mark.asyncio
async def test_coordinator_refresh_defaults_missing_schedule_status(
    hass, bypass_get_data
):
    """A schedule with no status is given the library default rather than crashing."""
    coordinator: PodPointDataUpdateCoordinator = await subject(hass)

    await coordinator.async_refresh()

    pod: Pod = coordinator.data[0]
    assert len(pod.charge_schedules) > 0

    # Simulate the API response that caused the crash
    pod.charge_schedules[0].status = None

    coordinator._PodPointDataUpdateCoordinator__default_missing_schedule_statuses(
        coordinator._PodPointDataUpdateCoordinator__pods_with_schedules()
    )

    schedule = pod.charge_schedules[0]
    assert schedule.status is not None
    assert schedule.is_active is False

    # The two call sites that used to raise
    assert schedule.dict["status"]["is_active"] is False
    assert pod.dict is not None


# The user carries its own nested Pod at user.unit.pod, with its own schedules, which
# sensor.py reads via `attrs.update(user.dict)`. That is a second route to the same
# crash, and it fires on every coordinator refresh rather than at setup:
#   File "custom_components/pod_point/sensor.py", line 663, in __update_attrs
#     attrs.update(user.dict)
@pytest.mark.asyncio
async def test_coordinator_refresh_defaults_user_pod_schedule_status(
    hass, bypass_get_data
):
    """A null status on the user's own nested pod is defaulted too."""
    coordinator: PodPointDataUpdateCoordinator = await subject(hass)

    await coordinator.async_refresh()

    user_pod = getattr(getattr(coordinator.user, "unit", None), "pod", None)
    if user_pod is None or not user_pod.charge_schedules:
        pytest.skip("user fixture has no nested pod schedules")

    user_pod.charge_schedules[0].status = None

    coordinator._PodPointDataUpdateCoordinator__default_missing_schedule_statuses(
        coordinator._PodPointDataUpdateCoordinator__pods_with_schedules()
    )

    assert user_pod.charge_schedules[0].status is not None
    assert coordinator.user.dict is not None

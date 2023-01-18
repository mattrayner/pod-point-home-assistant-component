"""Global fixtures for pod_point integration."""
# Fixtures allow you to replace functions with a Mock object. You can perform
# many options via the Mock to reflect a particular behavior from the original
# function that you want to see without going through the function's actual logic.
# Fixtures can either be passed into tests as parameters, or if autouse=True, they
# will automatically be used across all tests.
#
# Fixtures that are defined in conftest.py are available across all tests. You can also
# define fixtures within a particular test file to scope them locally.
#
# pytest_homeassistant_custom_component provides some fixtures that are provided by
# Home Assistant core. You can find those fixture definitions here:
# https://github.com/MatthewFlamm/pytest-homeassistant-custom-component/blob/master/pytest_homeassistant_custom_component/common.py
#
# See here for more info: https://docs.pytest.org/en/latest/fixture.html (note that
# pytest includes fixtures OOB which you can use as defined on this page)
from unittest.mock import patch

from .fixtures import CHARGES_COMPLETE_FIXTURE, POD_COMPLETE_FIXTURE, FIRMWARE_COMPLETE_FIXTURE, USER_COMPLETE_FIXTURE

from podpointclient.factories import PodFactory, ChargeFactory, FirmwareFactory, UserFactory
from podpointclient.errors import AuthError

import pytest

pytest_plugins = "pytest_homeassistant_custom_component"


# This fixture enables loading custom integrations in all tests.
# Remove to enable selective use of this fixture
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
    ):
        yield


# This fixture, when used, will result in calls to async_get_data to return None. To have the call
# return a value, we would add the `return_value=<VALUE_TO_RETURN>` parameter to the patch call.
@pytest.fixture(name="bypass_get_data")
def bypass_get_data_fixture():
    """Skip calls to get data from API."""

    pod_factory = PodFactory()
    pods = pod_factory.build_pods({"pods": [POD_COMPLETE_FIXTURE]})
    pod = pods[0]
    charge_factory = ChargeFactory()
    charges = charge_factory.build_charges(CHARGES_COMPLETE_FIXTURE)
    firmware_factory = FirmwareFactory()
    firmware = firmware_factory.build_firmwares(FIRMWARE_COMPLETE_FIXTURE)
    user_factory = UserFactory()
    user = user_factory.build_user(USER_COMPLETE_FIXTURE)

    with patch(
        "podpointclient.client.PodPointClient.async_get_all_pods", return_value=pods
    ), patch(
        "podpointclient.client.PodPointClient.async_get_pod", return_value=pod
    ), patch(
        "podpointclient.client.PodPointClient.async_set_schedule", return_value=True
    ), patch(
        "podpointclient.client.PodPointClient.async_get_all_charges",
        return_value=charges,
    ), patch(
        "podpointclient.client.PodPointClient.async_credentials_verified",
        return_value=True,
    ), patch(
        "podpointclient.client.PodPointClient.async_get_firmware",
        return_value=firmware,
    ), patch(
        "podpointclient.client.PodPointClient.async_get_user",
        return_value=user,
    ):
        yield


# In this fixture, we are forcing calls to async_get_data to raise an Exception. This is useful
# for exception handling.
@pytest.fixture(name="error_on_get_data")
def error_get_data_fixture():
    """Simulate error when retrieving data from API."""
    user_factory = UserFactory()
    user = user_factory.build_user(USER_COMPLETE_FIXTURE)

    with patch(
        "podpointclient.client.PodPointClient.async_get_pods",
        side_effect=AuthError,
    ), patch(
        "podpointclient.client.PodPointClient.async_get_user",
        return_value=user,
    ):
        yield

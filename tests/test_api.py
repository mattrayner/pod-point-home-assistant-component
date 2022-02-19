"""Tests for integration_blueprint api."""
import asyncio

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .fixtures import POD_COMPLETE_FIXTURE

from custom_components.pod_point.api import PodPointApiClient


async def test_api(hass, aioclient_mock, caplog):
    """Test API calls."""

    # To test the api submodule, we first create an instance of our API client
    api = PodPointApiClient("test", "test", async_get_clientsession(hass))

    # Use aioclient_mock which is provided by `pytest_homeassistant_custom_components`
    # to mock responses to aiohttp requests. In this case we are telling the mock to
    # return {"test": "test"} when a `GET` call is made to the specified URL. We then
    # call `async_get_data` which will make that `GET` request.
    pod_data = POD_COMPLETE_FIXTURE

    success_fixture = {
        "pods": [pod_data],
        "meta": {
            "pagination": {
                "current_page": 1,
                "per_page": 1,
                "page_count": 1,
                "item_count": 1,
            }
        },
    }

    aioclient_mock.post(
        "https://api.pod-point.com/v4/auth",
        json={"access_token": "1234", "expires_in": 1234},
    )
    aioclient_mock.post(
        "https://api.pod-point.com/v4/sessions", json={"sessions": {"user_id": "1234"}}
    )
    aioclient_mock.get(
        "https://api.pod-point.com/v4/users/1234/pods?perpage=all&include=statuses,price,model,unit_connectors,charge_schedules",
        json=success_fixture,
    )

    assert await api.async_get_pods() == {
        "meta": {
            "pagination": {
                "current_page": 1,
                "item_count": 1,
                "page_count": 1,
                "per_page": 1,
            }
        },
        "pods": [
            {
                "address_id": 1234,
                "charge_schedules": [
                    {
                        "end_day": 2,
                        "end_time": "00:00:00",
                        "start_day": 1,
                        "start_time": "06:00:00",
                        "status": {"is_active": False},
                        "uid": "24b342c8-8cbb-11ec-1111-0a9268fc07a0",
                    },
                    {
                        "end_day": 2,
                        "end_time": "07:00:00",
                        "start_day": 2,
                        "start_time": "02:00:00",
                        "status": {"is_active": False},
                        "uid": "24b8aeac-8cbb-11ec-2222-0a9268fc07a0",
                    },
                    {
                        "end_day": 3,
                        "end_time": "07:00:00",
                        "start_day": 3,
                        "start_time": "02:00:00",
                        "status": {"is_active": False},
                        "uid": "24bb6606-8cbb-11ec-3333-0a9268fc07a0",
                    },
                    {
                        "end_day": 4,
                        "end_time": "07:00:00",
                        "start_day": 4,
                        "start_time": "02:00:00",
                        "status": {"is_active": False},
                        "uid": "24be0168-8cbb-11ec-4444-0a9268fc07a0",
                    },
                    {
                        "end_day": 5,
                        "end_time": "07:00:00",
                        "start_day": 5,
                        "start_time": "02:00:00",
                        "status": {"is_active": False},
                        "uid": "24c089b0-8cbb-11ec-5555-0a9268fc07a0",
                    },
                    {
                        "end_day": 6,
                        "end_time": "07:00:00",
                        "start_day": 6,
                        "start_time": "02:00:00",
                        "status": {"is_active": False},
                        "uid": "24c346aa-8cbb-11ec-6666-0a9268fc07a0",
                    },
                    {
                        "end_day": 7,
                        "end_time": "07:00:00",
                        "start_day": 7,
                        "start_time": "02:00:00",
                        "status": {"is_active": False},
                        "uid": "24c6bf10-8cbb-11ec-7777-0a9268fc07a0",
                    },
                ],
                "commissioned_at": "2022-01-25T09:00:00+00:00",
                "contactless_enabled": False,
                "created_at": "2022-02-13T10:39:05+00:00",
                "description": "",
                "evZone": False,
                "home": True,
                "id": 12234,
                "last_contact_at": "2022-02-15T11:18:56+00:00",
                "location": {"lat": 0.12345, "lng": 2.45678901},
                "model": {
                    "id": 123,
                    "image_url": None,
                    "name": "S7-UC-03-ACA",
                    "supports_contactless": False,
                    "supports_ocpp": False,
                    "supports_payg": False,
                    "vendor": "Pod Point",
                },
                "name": None,
                "payg": False,
                "ppid": "PSL-123456",
                "price": None,
                "public": False,
                "statuses": [
                    {
                        "door": "A",
                        "door_id": 1,
                        "id": 2,
                        "key_name": "charging",
                        "label": "Charging",
                        "name": "Charging",
                    }
                ],
                "timezone": "UTC",
                "unit_connectors": [
                    {
                        "connector": {
                            "charge_method": "Single Phase " "AC",
                            "current": 32,
                            "door": "A",
                            "door_id": 1,
                            "has_cable": False,
                            "id": 123,
                            "power": 7,
                            "socket": {
                                "description": "Type " "2 " "socket",
                                "ocpp_code": 3,
                                "ocpp_name": "sType2",
                                "type": "IEC 62196-2 " "Type 2",
                            },
                            "voltage": 230,
                        }
                    }
                ],
                "unit_id": 123456,
            }
        ],
    }

    # We do the sax me for `async_set_title`. Note the difference in the mock call
    # between the previous step and this one. We use `patch` here instead of `get`
    # because we know that `async_set_title` calls `api_wrapper` with `patch` as the
    # first parameter
    aioclient_mock.post("https://api.pod-point.com/v4/units/123456/charge-schedules")
    assert await api.async_set_schedule(True, "12345") is None

    # In order to get 100% coverage, we need to test `api_wrapper` to test the code
    # that isn't already called by `async_get_data` and `async_set_title`. Because the
    # only logic that lives inside `api_wrapper` that is not being handled by a third
    # party library (aiohttp) is the exception handling, we also want to simulate
    # raising the exceptions to ensure that the function handles them as expected.
    # The caplog fixture allows access to log messages in tests. This is particularly
    # useful during exception handling testing since often the only action as part of
    # exception handling is a logging statement
    caplog.clear()
    aioclient_mock.put(
        "https://jsonplaceholder.typicode.com/posts/1", exc=asyncio.TimeoutError
    )
    assert (
        await api.api_wrapper("put", "https://jsonplaceholder.typicode.com/posts/1")
        is None
    )
    assert (
        len(caplog.record_tuples) == 1
        and "Timeout error fetching information from" in caplog.record_tuples[0][2]
    )

    caplog.clear()
    aioclient_mock.post(
        "https://jsonplaceholder.typicode.com/posts/1", exc=aiohttp.ClientError
    )
    assert (
        await api.api_wrapper("post", "https://jsonplaceholder.typicode.com/posts/1")
        is None
    )
    assert (
        len(caplog.record_tuples) == 1
        and "Error fetching information from" in caplog.record_tuples[0][2]
    )

    caplog.clear()
    aioclient_mock.post("https://jsonplaceholder.typicode.com/posts/2", exc=Exception)
    assert (
        await api.api_wrapper("post", "https://jsonplaceholder.typicode.com/posts/2")
        is None
    )
    assert (
        len(caplog.record_tuples) == 1
        and "Something really wrong happened!" in caplog.record_tuples[0][2]
    )

    caplog.clear()
    aioclient_mock.post("https://jsonplaceholder.typicode.com/posts/3", exc=TypeError)
    assert (
        await api.api_wrapper("post", "https://jsonplaceholder.typicode.com/posts/3")
        is None
    )
    assert (
        len(caplog.record_tuples) == 1
        and "Error parsing information from" in caplog.record_tuples[0][2]
    )

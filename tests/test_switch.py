# """Test integration_blueprint switch."""
# import asyncio

# import aiohttp
# from homeassistant.helpers.aiohttp_client import async_get_clientsession
# from .fixtures import POD_COMPLETE_FIXTURE
# from unittest.mock import call, patch

# from homeassistant.components.switch import SERVICE_TURN_OFF, SERVICE_TURN_ON
# from homeassistant.const import ATTR_ENTITY_ID
# from pytest_homeassistant_custom_component.common import MockConfigEntry

# from custom_components.pod_point import async_setup_entry
# from custom_components.pod_point.const import DEFAULT_NAME, DOMAIN, SWITCH

# from .const import MOCK_CONFIG


# async def test_switch_services(hass, aioclient_mock):
#     """Test switch services."""
#     # Create a mock entry so we don't have to go through config flow
#     config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
#     assert await async_setup_entry(hass, config_entry)
#     await hass.async_block_till_done()

#         # Use aioclient_mock which is provided by `pytest_homeassistant_custom_components`
#     # to mock responses to aiohttp requests. In this case we are telling the mock to
#     # return {"test": "test"} when a `GET` call is made to the specified URL. We then
#     # call `async_get_data` which will make that `GET` request.
#     pod_data = POD_COMPLETE_FIXTURE

#     success_fixture = {
#         "pods": [pod_data],
#         "meta": {
#             "pagination": {
#                 "current_page": 1,
#                 "per_page": 1,
#                 "page_count": 1,
#                 "item_count": 1,
#             }
#         },
#     }

#     aioclient_mock.post(
#         "https://api.pod-point.com/v4/auth",
#         json={"access_token": "1234", "expires_in": 1234},
#     )
#     aioclient_mock.post(
#         "https://api.pod-point.com/v4/sessions", json={"sessions": {"user_id": "1234"}}
#     )
#     aioclient_mock.get(
#         "https://api.pod-point.com/v4/users/1234/pods?perpage=all&include=statuses,price,model,unit_connectors,charge_schedules",
#         json=success_fixture,
#     )

#     # Functions/objects can be patched directly in test code as well and can be used to test
#     # additional things, like whether a function was called or what arguments it was called with
#     with patch(
#         "custom_components.pod_point.PodPointApiClient.async_set_schedule"
#     ) as title_func:
#         await hass.services.async_call(
#             SWITCH,
#             SERVICE_TURN_OFF,
#             service_data={ATTR_ENTITY_ID: f"{SWITCH}.{DEFAULT_NAME}_{SWITCH}"},
#             blocking=True,
#         )
#         assert title_func.called
#         assert title_func.call_args == call("foo")

#         title_func.reset_mock()

#         await hass.services.async_call(
#             SWITCH,
#             SERVICE_TURN_ON,
#             service_data={ATTR_ENTITY_ID: f"{SWITCH}.{DEFAULT_NAME}_{SWITCH}"},
#             blocking=True,
#         )
#         assert title_func.called
#         assert title_func.call_args == call("bar")

"""Sample API Client."""
import logging
import asyncio
import socket
from typing import Optional, Dict, Any, List
import aiohttp
import async_timeout
from datetime import datetime, timedelta

from .errors import PodPointAuthError, PodPointSessionError

from .const import BASE_API_URL

TIMEOUT = 10

_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class PodPointApiClient:
    """API Client for communicating with Pod Point."""

    def __init__(
        self, username: str, password: str, session: aiohttp.ClientSession
    ) -> None:
        """Pod Point API Client."""
        self._email = username
        self._password = password
        self._session = session
        self._access_token = None
        self._access_token_expiration = None
        self._user_id = None

    async def async_get_pods(self) -> List[Dict[str, Any]]:
        """Get pods from the API."""
        await self.async_check_access_token()

        path = f"/users/{self._user_id}/pods"
        url = f"{BASE_API_URL}{path}"

        _LOGGER.debug(url)

        includes = ["statuses", "price", "model", "unit_connectors", "charge_schedules"]
        params = {"perpage": "all", "include": ",".join(includes)}

        headers = self._auth_headers()

        response = await self.api_wrapper("get", url, params=params, headers=headers)

        _LOGGER.debug(response)

        return response

    async def async_get_pod(self, pod_id) -> Dict[str, Any]:
        """Get specific pod from the API."""
        pods = await self.async_get_pods()
        return next((item for item in await pods.json() if item["id"] == pod_id), None)

    async def async_set_schedule(self, enabled: bool, unit_id: int) -> None:
        """Send data from the API."""

        _LOGGER.info(
            f"Updating pod schedule for unit {unit_id}. Ebaling schedule: {enabled}"
        )

        await self.async_check_access_token()
        path = f"/units/{unit_id}/charge-schedules"
        url = f"{BASE_API_URL}{path}"

        headers = self._auth_headers()
        payload = self._schedule_data(enabled)

        _LOGGER.debug(url)
        _LOGGER.debug(headers)
        _LOGGER.debug(payload)

        response = await self.api_wrapper("put", url, data=payload, headers=headers)

        _LOGGER.debug(response)

        return response

    async def api_wrapper(
        self,
        method: str,
        url: str,
        data: dict = {},
        headers: dict = {},
        params: dict = {},
    ) -> dict:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(TIMEOUT):
                if method == "get":
                    return await self._session.get(url, headers=headers, params=params)

                elif method == "put":
                    return await self._session.put(url, headers=headers, json=data)

                elif method == "patch":
                    return await self._session.patch(url, headers=headers, json=data)

                elif method == "post":
                    return await self._session.post(url, headers=headers, json=data)

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)

    async def async_check_access_token(self) -> bool:
        access_token_set = (
            self._access_token is not None and self._access_token_expiration is not None
        )
        access_token_not_expired = (
            access_token_set and datetime.now() < self._access_token_expiration
        )

        if access_token_set and access_token_not_expired:
            return True
        else:
            _LOGGER.debug("Access token refresh required")
            success = await self.__async_update_access_token()

            if success:
                _LOGGER.debug(
                    f"Updated access token. New expiration: {self._access_token_expiration}"
                )

                success = await self.__async_create_session()
                if success is False:
                    _LOGGER.error("Error creating session")

            else:
                _LOGGER.error("Error updating access token")

            return success

    async def __async_update_access_token(self) -> bool:
        return_value = False

        _LOGGER.info("Updating Pod Point access token")

        url = f"{BASE_API_URL}/auth"
        payload = {"username": self._email, "password": self._password}

        try:
            response = await self.api_wrapper(
                "post", url, data=payload, headers=HEADERS
            )

            _LOGGER.debug(response)

            if response.status != 200:
                await self.__handle_response_error(response, PodPointAuthError)
            else:
                json = await response.json()
                self._access_token = json["access_token"]
                self._access_token_expiration = datetime.now() + timedelta(
                    seconds=json["expires_in"] - 10
                )
                return_value = True
        except KeyError as exception:
            _LOGGER.error(f"Error processing access token response: {exception}")
            await self.__handle_response_error(response, PodPointAuthError)

        return return_value

    async def __async_create_session(self) -> bool:
        _LOGGER.info("Creating session")

        url = f"{BASE_API_URL}/sessions"
        headers = self._auth_headers()
        payload = {"email": self._email, "password": self._password}

        return_value = False

        try:
            response = await self.api_wrapper(
                "post", url, data=payload, headers=headers
            )

            _LOGGER.debug(response)

            json = await response.json()

            if json["sessions"]:
                _LOGGER.debug("Setting user ID")
                self._user_id = json["sessions"]["user_id"]
                return_value = True
        except KeyError as exception:
            _LOGGER.error(f"Error processing session response {exception}")
            await self.__handle_response_error(response, PodPointSessionError)

        return return_value

    def _auth_headers(self) -> Dict[str, str]:
        auth_header = {"Authorization": f"Bearer {self._access_token}"}
        combined_headers = HEADERS.copy()
        combined_headers.update(auth_header)
        return combined_headers

    def _schedule_data(self, enabled: bool) -> Dict[str, List[Dict[str, Any]]]:
        schedules = []

        for i in range(7):
            day = i + 1

            schedules.append(
                {
                    "start_day": day,
                    "start_time": "00:00:00",
                    "end_day": day,
                    "end_time": "00:00:01",
                    "status": {"is_active": enabled},
                }
            )

        return {"data": schedules}

    async def __handle_response_error(self, response, error_class):
        status = response.status
        _LOGGER.error(f"Unexpected response when creating session ({status})")
        response = await response.text()
        _LOGGER.error(response)

        raise error_class(status, response)

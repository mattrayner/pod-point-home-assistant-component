"""
Data coordinator for pod point client
"""
import logging
from typing import List, Dict

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from podpointclient.client import PodPointClient
from podpointclient.pod import Pod
from podpointclient.charge import Charge
from podpointclient.errors import AuthError, SessionError, ApiConnectionError

from .const import (
    DOMAIN,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class PodPointDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self, hass: HomeAssistant, client: PodPointClient, scan_interval: int
    ) -> None:
        """Initialize."""
        self.api: PodPointClient = client
        self.platforms = []
        self.pods: List[Pod] = []
        self._charges = "all"
        self.pod_dict = None
        self.online = None

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=scan_interval)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            _LOGGER.debug("Updating pods and charges")
            self.pods: List[Pod] = await self.api.async_get_pods()
            self.pod_dict = None

            _LOGGER.debug("Pods: %s", len(self.pods))

            charges: List[Charge] = await self.api.async_get_charges(
                per_page=self._charges
            )
            home_charges: List[Charge] = list(
                filter(lambda charge: charge.location.home is True, charges)
            )

            _LOGGER.debug("Charges: %s", len(home_charges))

            pods_by_id = self.__group_pods_by_unit_id()

            charge: Charge
            for charge in home_charges:
                unit_id = charge.pod.id
                pod: Pod = pods_by_id.get(unit_id, None)

                if pod is None:
                    continue

                pod.charges.append(charge)
                pod.total_kwh = pod.total_kwh + charge.kwh_used
                pod.total_charge_seconds = charge.duration

                if charge.ends_at is None:
                    pod.current_kwh = charge.kwh_used

            self.pods = list(pods_by_id.values())

            if self.online is False:
                _LOGGER.info("Connection to Pod Point re-established.")
            self.online = True

            return self.pods

        except ApiConnectionError as exception:
            if self.online is not False:
                _LOGGER.warning("Unable to connect to Pod Point. (%s)", exception)

            self.online = False
            _LOGGER.debug(exception)

            raise UpdateFailed(
                "Unable to connect to Pod Point. Retrying"
            ) from exception

        except (AuthError, SessionError) as exception:
            _LOGGER.debug("Recommending re-auth: %s", exception)

            raise ConfigEntryAuthFailed(
                "There was a problem logging in with your account."
            ) from exception
        except Exception as exception:
            _LOGGER.warning(
                "Recieved an unexpected exception when updating data from Pod Point. \
If this issue persists, please contact the developer."
            )
            _LOGGER.error(exception)
            raise UpdateFailed() from exception

    def __group_pods_by_unit_id(self) -> Dict[int, Pod]:
        pod_dict: Dict[int, Pod] = {}
        for pod in self.pods:
            pod_dict[pod.unit_id] = pod

        self.pod_dict = pod_dict
        return self.pod_dict

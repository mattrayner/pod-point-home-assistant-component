"""
Custom integration to integrate integration_blueprint with Home Assistant.

For more details about this integration, please refer to
https://github.com/custom-components/integration_blueprint
"""
import asyncio
from datetime import timedelta
import logging
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from podpointclient.client import PodPointClient
from podpointclient.pod import Pod
from podpointclient.charge import Charge
from podpointclient.errors import AuthError, SessionError

from typing import List, Dict

from .const import (
    APP_IMAGE_URL_BASE,
    CONF_PASSWORD,
    CONF_EMAIL,
    CONF_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
    DEFAULT_SCAN_INTERVAL,
)


_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    email = entry.data.get(CONF_EMAIL)
    password = entry.data.get(CONF_PASSWORD)

    session = async_get_clientsession(hass)
    client = PodPointClient(username=email, password=password, session=session)

    try:
        scan_interval = timedelta(seconds=entry.options[CONF_SCAN_INTERVAL])
    except KeyError:
        scan_interval = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

    coordinator = PodPointDataUpdateCoordinator(
        hass, client=client, scan_interval=scan_interval
    )
    await coordinator.async_config_entry_first_refresh()

    should_cache = False
    files_path = Path(__file__).parent / "static"
    if hass.http:
        hass.http.register_static_path(
            APP_IMAGE_URL_BASE, str(files_path), should_cache
        )

    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


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

                if charge.ends_at is None:
                    pod.current_kwh = charge.kwh_used

            self.pods = list(pods_by_id.values())
            return self.pods
        except (AuthError, SessionError) as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except Exception as exception:
            _LOGGER.error(exception)
            raise UpdateFailed() from exception

    def __group_pods_by_unit_id(self) -> Dict[int, Pod]:
        if self.pod_dict is not None:
            return self.pod_dict

        pod_dict: Dict[int, Pod] = {}
        for pod in self.pods:
            pod_dict[pod.unit_id] = pod

        self.pod_dict = pod_dict
        return self.pod_dict


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

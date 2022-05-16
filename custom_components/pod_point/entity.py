"""PodPointEntity class"""
import logging
from typing import Any, Dict, List
from datetime import datetime, timedelta

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback
from homeassistant.config_entries import ConfigEntry

from podpointclient.pod import Pod
from podpointclient.schedule import Schedule

_LOGGER: logging.Logger = logging.getLogger(__package__)

from .const import (
    ATTR_STATE_AVAILABLE,
    ATTR_STATE_CHARGING,
    DOMAIN,
    NAME,
    ATTRIBUTION,
    ATTR_STATE_RANKING,
    ATTR_STATE,
    ATTR_STATE_WAITING,
    ATTR_STATE_CONNECTED_WAITING,
    APP_IMAGE_URL_BASE,
    CHARGING_FLAG,
)


class PodPointEntity(CoordinatorEntity):
    """Pod Point Entity"""

    def __init__(self, coordinator, config_entry: ConfigEntry, idx: int):
        super().__init__(coordinator)
        self.pod_id = idx
        self.config_entry = config_entry
        self.extra_attrs = {}

        self.__update_attrs()

    def __update_attrs(self):
        pod: Pod = self.pod

        attrs = {
            "attribution": ATTRIBUTION,
            "id": pod.id,
            "integration": DOMAIN,
            "suggested_area": "Outside",
            "total_kwh": pod.total_kwh,
            "current_kwh": pod.current_kwh,
        }

        attrs.update(pod.dict)

        state = None
        for status in pod.statuses:
            state = self.compare_state(state, status.key_name)

        is_available_state = state == ATTR_STATE_AVAILABLE
        is_charging_state = state == ATTR_STATE_CHARGING
        charging_not_allowed = self.charging_allowed is False
        should_be_waiting_state = is_available_state and charging_not_allowed
        should_be_connected_waiting_state = is_charging_state and charging_not_allowed

        if should_be_waiting_state:
            state = ATTR_STATE_WAITING

        if should_be_connected_waiting_state:
            state = ATTR_STATE_CONNECTED_WAITING

        attrs[ATTR_STATE] = state

        self._attr_state = state

        self.extra_attrs = attrs

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.__update_attrs()
        self.async_write_ha_state()

    @property
    def pod(self) -> Pod:
        """Return the underlying pod that drives this entity"""
        pod: Pod = self.coordinator.data[self.pod_id]
        return pod

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        if self.pod.id:
            return f"{DOMAIN}_{self.pod.id}_{self.pod.ppid}"
        else:
            return self.config_entry.entry_id

    @property
    def device_info(self) -> Dict[str, Any]:
        name = NAME
        if len(self.psl) > 0:
            name = self.psl

        return {
            "identifiers": {(DOMAIN, self.pod.ppid)},
            "name": name,
            "model": self.model,
            "manufacturer": NAME,
        }

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        return self.extra_attrs

    @property
    def charging_allowed(self) -> bool:
        """Is charging allowed by schedule?"""
        pod: Pod = self.coordinator.data[self.pod_id]
        schedules: List[Schedule] = pod.charge_schedules

        # No schedules are found, we will assume we can charge
        if len(schedules) <= 0:
            return True

        weekday = datetime.today().weekday() + 1
        schedule_for_day: Schedule = next(
            (schedule for schedule in schedules if schedule.start_day == weekday),
            None,
        )

        # If no schedule is set for our day, return False early, there should always be a
        # schedule for each day, even if it is inactive
        if schedule_for_day is None:
            return False

        schedule_active = schedule_for_day.is_active

        # If schedule_active is None, there was a problem. we will return False
        if schedule_active is None:
            return False

        # If the schedule for this day is not active, we can charge
        if schedule_active is False:
            return True

        start_time = list(map(lambda x: int(x), schedule_for_day.start_time.split(":")))
        start_date = datetime.now().replace(
            hour=start_time[0], minute=start_time[1], second=start_time[2]
        )

        end_time = list(map(lambda x: int(x), schedule_for_day.end_time.split(":")))
        end_day = schedule_for_day.end_day
        end_date = None
        if end_day < weekday:
            # roll into next week
            end_time = end_date = datetime.now().replace(
                hour=end_time[0], minute=end_time[1], second=end_time[2]
            )

            # How many days do we add to the current date to get to the desired end day?
            day_offset = (7 - weekday) + (end_day - 1)
            end_date = end_time + timedelta(days=day_offset)
        elif end_day > weekday:
            day_offset = end_day - weekday

            end_time = end_date = datetime.now().replace(
                hour=end_time[0], minute=end_time[1], second=end_time[2]
            )
            end_date = end_time + timedelta(days=day_offset)
        else:
            end_date = datetime.now().replace(
                hour=end_time[0], minute=end_time[1], second=end_time[2]
            )

        # Problem creating the end_date, so we will exit with False
        if end_date is None:
            return False

        in_range = start_date <= datetime.now() <= end_date

        # Are we within the range for today?
        return in_range

    @property
    def unit_id(self) -> int:
        """Return the unit id - used for schedule updates"""
        return self.pod.unit_id

    @property
    def psl(self) -> str:
        """Return the PSL - used for identifying multiple pods"""
        return self.pod.ppid

    @property
    def model(self) -> str:
        """Return the model of our podpoint"""
        return self.pod.model.name

    @property
    def image(self) -> str:
        """Return the image url for this model"""
        return self.__pod_image(self.model)

    @property
    def connected(self) -> bool:
        """Returns true if pod is connected to a vehicle"""
        status = self.extra_state_attributes.get(ATTR_STATE, "")
        return status in (CHARGING_FLAG, ATTR_STATE_CONNECTED_WAITING)

    def compare_state(self, state, pod_state) -> str:
        """Given two states, which one is most important"""
        ranking = ATTR_STATE_RANKING

        # If pod state is None, but state is set, return the state
        if pod_state is None and state is not None:
            return state
        elif state is None and pod_state is not None:
            return pod_state

        try:
            state_rank = ranking.index(state)
        except ValueError:
            state_rank = 100

        try:
            pod_rank = ranking.index(pod_state)
        except ValueError:

            pod_rank = 100

        winner = state if state_rank >= pod_rank else pod_state

        return winner

    def __pod_image(self, model: str) -> str:
        if model is None:
            return None

        model_slug = self.__model_slug()
        model_type = model_slug[0]
        model_id = model_slug[1]

        if model_type == "UP":
            model_type = "UC"

        if model_type == "1C":
            model_type = "2C"

        img = model_type
        if model_id == "03":
            img = f"{model_type}-{model_id}"

        return f"{APP_IMAGE_URL_BASE}/{img.lower()}.png"

    def __model_slug(self) -> List[str]:
        return self.model.upper()[3:8].split("-")

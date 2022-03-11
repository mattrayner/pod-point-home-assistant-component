"""PodPointEntity class"""
import logging
from typing import Any, Dict, List
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback
from datetime import datetime, timedelta
from podpointclient.pod import Pod
from podpointclient.schedule import Schedule

_LOGGER: logging.Logger = logging.getLogger(__package__)

from .const import (
    ATTR_STATE_AVAILABLE,
    ATTR_STATE_CHARGING,
    DOMAIN,
    NAME,
    ATTRIBUTION,
    ATTR_COMMISSIONED,
    ATTR_CONNECTOR,
    ATTR_CONNECTOR_CHARGE_METHOD,
    ATTR_CONNECTOR_CURRENT,
    ATTR_CONNECTOR_DOOR,
    ATTR_CONNECTOR_DOOR_ID,
    ATTR_CONNECTOR_HAS_CABLE,
    ATTR_CONNECTOR_ID,
    ATTR_CONNECTOR_POWER,
    ATTR_CONNECTOR_SOCKET,
    ATTR_CONNECTOR_SOCKET_OCPP_CODE,
    ATTR_CONNECTOR_SOCKET_OCPP_NAME,
    ATTR_CONNECTOR_SOCKET_TYPE,
    ATTR_CONNECTOR_VOLTAGE,
    ATTR_CONTACTLESS_ENABLED,
    ATTR_CREATED,
    ATTR_EVZONE,
    ATTR_HOME,
    ATTR_ID,
    ATTR_LAST_CONTACT,
    ATTR_LAT,
    ATTR_LNG,
    ATTR_MODEL,
    ATTR_PAYG,
    ATTR_PRICE,
    ATTR_PSL,
    ATTR_PUBLIC,
    ATTR_STATUS,
    ATTR_STATUS_DOOR,
    ATTR_STATUS_DOOR_ID,
    ATTR_STATUS_KEY_NAME,
    ATTR_STATUS_LABEL,
    ATTR_STATUS_NAME,
    ATTR_TIMEZONE,
    ATTR_UNIT_ID,
    ATTR_STATE_RANKING,
    ATTR_STATE,
    ATTR_STATE_WAITING,
    ATTR_STATE_CONNECTED_WAITING,
    APP_IMAGE_URL_BASE,
)


class PodPointEntity(CoordinatorEntity):
    """Pod Point Entity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.pod_id = None
        self.config_entry = config_entry
        self.extra_attrs = {}

        self.__update_attrs

    def __update_attrs(self):
        pod: Pod = self.pod

        attrs = {
            "attribution": ATTRIBUTION,
            "id": pod.id,
            "integration": DOMAIN,
            "suggested_area": "Outside",
        }

        attrs.update(pod.dict)

        state = None
        for status in pod.statuses:
            state = self.compare_state(state, status.key_name)

        _LOGGER.debug(state)
        _LOGGER.debug("Charging allowed: %s", self.charging_allowed)

        is_available_state = state == ATTR_STATE_AVAILABLE
        is_charging_state = state == ATTR_STATE_CHARGING
        charging_not_allowed = self.charging_allowed is False
        should_be_waiting_state = is_available_state and charging_not_allowed
        should_be_connected_waiting_state = is_charging_state and charging_not_allowed

        _LOGGER.debug("Is charging state: %s", is_charging_state)
        _LOGGER.debug("Charging not allowed: %s", charging_not_allowed)
        _LOGGER.debug("Should be waiting state: %s", should_be_waiting_state)

        if should_be_waiting_state:
            state = ATTR_STATE_WAITING

        if should_be_connected_waiting_state:
            state = ATTR_STATE_CONNECTED_WAITING

        _LOGGER.info("Computed state: %s", state)

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
        pod: Pod = self.coordinator.data[self.pod_id]
        return pod

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id

    @property
    def device_info(self) -> Dict[str, Any]:
        name = NAME
        if len(self.psl) > 0:
            name = self.psl

        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": name,
            "model": self.model,
            "manufacturer": NAME,
        }

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        # return {
        #     "attribution": ATTRIBUTION,
        #     "id": str(self.coordinator.data.get("id")),
        #     "integration": DOMAIN,
        # }
        return self.extra_attrs

    @property
    def charging_allowed(self) -> bool:
        """Is charging allowed by schedule?"""
        _LOGGER.info("Getting schedules")

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

        _LOGGER.debug("Weekday %s", weekday)
        _LOGGER.debug("Schedule for day:")
        _LOGGER.debug(schedule_for_day)

        # If no schedule is set for our day, return False early, there should always be a
        # schedule for each day, even if it is inactive
        if schedule_for_day is None:
            return False

        schedule_active = schedule_for_day.is_active

        # If schedule_active is None, there was a problem. we will return False
        if schedule_active is None:
            return False

        _LOGGER.debug("Schedule active: %s", schedule_active)

        # If the schedule for this day is not active, we can charge
        if schedule_active is False:
            return True

        start_time = list(map(lambda x: int(x), schedule_for_day.start_time.split(":")))
        start_date = datetime.now().replace(
            hour=start_time[0], minute=start_time[1], second=start_time[2]
        )

        _LOGGER.debug("start: %s", start_date)

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

        _LOGGER.debug("end: %s", end_date)

        # Problem creating the end_date, so we will exit with False
        if end_date is None:
            return False

        in_range = start_date <= datetime.now() <= end_date

        _LOGGER.debug(f"in range: %s", in_range)

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

        _LOGGER.debug("Winning state: %s from %s and %s", winner, state, pod_state)

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
        _LOGGER.debug(self.model)
        return self.model.upper()[3:8].split("-")

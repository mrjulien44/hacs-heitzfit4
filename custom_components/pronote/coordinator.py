"""Data update coordinator for the heitzfit4 integration."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import logging
from .heitzfit4_helper import *
from .heitzfit4_formatter import *
import re
from zoneinfo import ZoneInfo

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import TimestampDataUpdateCoordinator


from .const import (
    ACTIVITY_MAX_DAYS,
    ACTIVITY_NEXT_DAY_SEARCH_LIMIT,
    RESERVATION_MAX_DAYS,
    # INFO_SURVEY_LIMIT_MAX_DAYS,
    EVENT_TYPE,
    DEFAULT_REFRESH_INTERVAL,
    DEFAULT_ALARM_OFFSET,
)

_LOGGER = logging.getLogger(__name__)


# def get_grades(client):
#     grades = client.current_period.grades
#     return sorted(grades, key=lambda grade: grade.date, reverse=True)


# def get_absences(client):
#     absences = client.current_period.absences
#     return sorted(absences, key=lambda absence: absence.from_date, reverse=True)


# def get_delays(client):
#     delays = client.current_period.delays
#     return sorted(delays, key=lambda delay: delay.date, reverse=True)


# def get_averages(client):
#     averages = client.current_period.averages
#     return averages


# def get_punishments(client):
#     punishments = client.current_period.punishments
#     return sorted(
#         punishments,
#         key=lambda punishment: punishment.given.strftime("%Y-%m-%d"),
#         reverse=True,
#     )


# def get_evaluations(client):
#     evaluations = client.current_period.evaluations
#     evaluations = sorted(evaluations, key=lambda evaluation: (evaluation.name))
#     return sorted(evaluations, key=lambda evaluation: (evaluation.date), reverse=True)


class heitzfit4DataUpdateCoordinator(TimestampDataUpdateCoordinator):
    """Data update coordinator for the heitzfit4 integration."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=entry.title,
            update_interval=timedelta(
                minutes=entry.options.get("refresh_interval", DEFAULT_REFRESH_INTERVAL)
            ),
        )
        self.config_entry = entry

    async def _async_update_data(self) -> dict[Platform, dict[str, Any]]:
        """Get the latest data from heitzfit4 and updates the state."""
        today = date.today()
        previous_data = None if self.data is None else self.data.copy()

        config_data = self.config_entry.data
        self.data = {
            # "account_type": config_data["account_type"],
            "sensor_prefix": None,
            # "child_info": None,
            "activitys_today": [],
            "activitys_tomorrow": [],
            "activitys_next_day": [],
            "activitys_period": [],
            "ical_url": None,
            # "grades": [],
            # "averages": [],
            "reservation": [],
            "reservation_period": [],
            # "absences": [],
            # "delays": [],
            # "evaluations": [],
            # "punishments": [],
            # "menus": [],
            # "information_and_surveys": [],
            "next_alarm": None,
        }

        client = await self.hass.async_add_executor_job(get_heitzfit4_client, config_data)

        if client is None:
            _LOGGER.error("Unable to init heitzfit4 client")
            return None

        # should be moved to heitzfit4_helper but won't work
        # if config_data["connection_type"] == "qrcode":
        #     new_data = config_data.copy()
        #     new_data.update({"qr_code_password": client.password})
        #     self.hass.config_entries.async_update_entry(
        #         self.config_entry, data=new_data
        #     )

        # child_info = client.info

        # if config_data["account_type"] == "parent":
        #     client.set_child(config_data["child"])
        #     child_info = client._selected_child

        # if child_info is None:
        #     return None

        # self.data["child_info"] = child_info
        # self.data["sensor_prefix"] = re.sub("[^A-Za-z]", "_", child_info.name.lower())

        # activitys
        try:
            activitys_today = await self.hass.async_add_executor_job(
                client.activitys, today
            )
            self.data["activitys_today"] = sorted(
                activitys_today, key=lambda activity: activity.start
            )
        except Exception as ex:
            self.data["activitys_today"] = None
            _LOGGER.info("Error getting activitys_today from heitzfit4: %s", ex)

        try:
            activitys_tomorrow = await self.hass.async_add_executor_job(
                client.activitys, today + timedelta(days=1)
            )
            self.data["activitys_tomorrow"] = sorted(
                activitys_tomorrow, key=lambda activity: activity.start
            )
        except Exception as ex:
            self.data["activitys_tomorrow"] = None
            _LOGGER.info("Error getting activitys_tomorrow from heitzfit4: %s", ex)

        activitys_period = None
        delta = ACTIVITY_MAX_DAYS
        while True and delta > 0:
            try:
                activitys_period = await self.hass.async_add_executor_job(
                    client.activitys, today, today + timedelta(days=delta)
                )
            except Exception as ex:
                _LOGGER.debug(
                    f"No activitys at: {delta} from today, searching best earlier alternative ({ex})"
                )
            if activitys_period:
                break
            delta = delta - 1
        _LOGGER.debug(
            f"activitys found at: {delta} days, for a maximum of {ACTIVITY_MAX_DAYS} from today"
        )
        self.data["activitys_period"] = (
            sorted(activitys_period, key=lambda activity: activity.start)
            if activitys_period is not None
            else None
        )

        if (
            self.data["activitys_tomorrow"] is not None
            and len(self.data["activitys_tomorrow"]) > 0
        ):
            self.data["activitys_next_day"] = self.data["activitys_tomorrow"]
        else:
            try:
                delta = 2
                while True and delta < ACTIVITY_NEXT_DAY_SEARCH_LIMIT:
                    activitys_nextday = await self.hass.async_add_executor_job(
                        client.activitys, today + timedelta(days=delta)
                    )
                    if activitys_nextday:
                        break
                    else:
                        activitys_nextday = None
                        del activitys_nextday
                    delta = delta + 1
                self.data["activitys_next_day"] = sorted(
                    activitys_nextday, key=lambda activity: activity.start
                )
                activitys_nextday = None
                del activitys_nextday
            except Exception as ex:
                self.data["activitys_next_day"] = None
                _LOGGER.info("Error getting activitys_next_day from heitzfit4: %s", ex)

        next_alarm = None
        tz = ZoneInfo(self.hass.config.time_zone)
        today_start_at = get_day_start_at(self.data["activitys_today"])
        next_day_start_at = get_day_start_at(self.data["activitys_next_day"])
        if today_start_at or next_day_start_at:
            alarm_offset = self.config_entry.options.get(
                "alarm_offset", DEFAULT_ALARM_OFFSET
            )
            if today_start_at is not None:
                todays_alarm = today_start_at - timedelta(minutes=alarm_offset)
                if datetime.now() <= todays_alarm:
                    next_alarm = todays_alarm
            if next_alarm is None and next_day_start_at is not None:
                next_alarm = next_day_start_at - timedelta(minutes=alarm_offset)
        if next_alarm is not None:
            next_alarm = next_alarm.replace(tzinfo=tz)

        self.data["next_alarm"] = next_alarm

        # # Grades
        # try:
        #     self.data["grades"] = await self.hass.async_add_executor_job(
        #         get_grades, client
        #     )
        #     self.compare_data(
        #         previous_data,
        #         "grades",
        #         ["date", "subject", "grade_out_of"],
        #         "new_grade",
        #         format_grade,
        #     )
        # except Exception as ex:
        #     self.data["grades"] = None
        #     _LOGGER.info("Error getting grades from heitzfit4: %s", ex)

        # # Averages
        # try:
        #     self.data["averages"] = await self.hass.async_add_executor_job(
        #         get_averages, client
        #     )
        # except Exception as ex:
        #     self.data["averages"] = None
        #     _LOGGER.info("Error getting averages from heitzfit4: %s", ex)

        # reservation
        try:
            reservation = await self.hass.async_add_executor_job(client.reservation, today)
            self.data["reservation"] = sorted(reservation, key=lambda activity: activity.date)
        except Exception as ex:
            self.data["reservation"] = None
            _LOGGER.info("Error getting reservation from heitzfit4: %s", ex)

        try:
            reservation_period = await self.hass.async_add_executor_job(
                client.reservation, today, today + timedelta(days=RESERVATION_MAX_DAYS)
            )
            self.data["reservation_period"] = sorted(
                reservation_period, key=lambda reservation: reservation.date
            )
        except Exception as ex:
            self.data["reservation_period"] = None
            _LOGGER.info("Error getting reservation_period from heitzfit4: %s", ex)

        # Information and Surveys
        # try:
        #     information_and_surveys = await self.hass.async_add_executor_job(
        #         client.information_and_surveys,
        #         today - timedelta(days=INFO_SURVEY_LIMIT_MAX_DAYS),
        #     )
        #     self.data["information_and_surveys"] = sorted(
        #         information_and_surveys,
        #         key=lambda information_and_survey: information_and_survey.creation_date,
        #         reverse=True,
        #     )
        # except Exception as ex:
        #     self.data["information_and_surveys"] = None
        #     _LOGGER.info("Error getting information_and_surveys from heitzfit4: %s", ex)

        # # Absences
        # try:
        #     self.data["absences"] = await self.hass.async_add_executor_job(
        #         get_absences, client
        #     )
        #     self.compare_data(
        #         previous_data, "absences", ["from", "to"], "new_absence", format_absence
        #     )
        # except Exception as ex:
        #     self.data["absences"] = None
        #     _LOGGER.info("Error getting absences from heitzfit4: %s", ex)

        # # Delays
        # try:
        #     self.data["delays"] = await self.hass.async_add_executor_job(
        #         get_delays, client
        #     )
        #     self.compare_data(
        #         previous_data, "delays", ["date", "minutes"], "new_delay", format_delay
        #     )
        # except Exception as ex:
        #     self.data["delays"] = None
        #     _LOGGER.info("Error getting delays from heitzfit4: %s", ex)

        # # Evaluations
        # try:
        #     self.data["evaluations"] = await self.hass.async_add_executor_job(
        #         get_evaluations, client
        #     )
        # except Exception as ex:
        #     self.data["evaluations"] = None
        #     _LOGGER.info("Error getting evaluations from heitzfit4: %s", ex)

        # # Punishments
        # try:
        #     self.data["punishments"] = await self.hass.async_add_executor_job(
        #         get_punishments, client
        #     )
        # except Exception as ex:
        #     self.data["punishments"] = None
        #     _LOGGER.info("Error getting punishments from heitzfit4: %s", ex)

        # iCal
        try:
            self.data["ical_url"] = await self.hass.async_add_executor_job(
                client.export_ical
            )
        except Exception as ex:
            _LOGGER.info("Error getting ical_url from heitzfit4: %s", ex)

        # Menus
        # try:
        #     self.data["menus"] = await self.hass.async_add_executor_job(
        #         client.menus, today, today + timedelta(days=7)
        #     )
        # except Exception as ex:
        #     self.data["menus"] = None
        #     _LOGGER.info("Error getting menus from heitzfit4: %s", ex)

        # return self.data

    def compare_data(
        self, previous_data, data_key, compare_keys, event_type, format_func
    ):
        if (
            previous_data is not None
            and previous_data[data_key] is not None
            and self.data[data_key] is not None
        ):
            not_found_items = []
            for item in self.data[data_key]:
                found = False
                for previous_item in previous_data[data_key]:
                    if {
                        key: format_func(previous_item)[key] for key in compare_keys
                    } == {key: format_func(item)[key] for key in compare_keys}:
                        found = True
                        break
                if found is False:
                    not_found_items.append(item)
            for not_found_item in not_found_items:
                self.trigger_event(event_type, format_func(not_found_item))

    def trigger_event(self, event_type, event_data):
        event_data = {
            # "child_name": self.data["child_info"].name,
            # "child_nickname": self.config_entry.options.get("nickname"),
            # "child_slug": self.data["sensor_prefix"],
            "type": event_type,
            "data": event_data,
        }
        self.hass.bus.async_fire(EVENT_TYPE, event_data)

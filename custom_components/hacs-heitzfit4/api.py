import aiohttp
import json

from datetime import date, timedelta, datetime
from typing import Any

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import TimestampDataUpdateCoordinator


from .const import (
    PLANNING_MAX_DAYS,
)

_LOGGER = logging.getLogger(__name__)

class Heitzfit4API:
    def __init__(self, club, username, password):
        self.club = club
        self.username = username
        self.password = password
        self.token = None
        self.clientId = None

    async def async_sign_in(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://app.heitzfit.com/c/3649/ws/api/auth/signin",
                json={
                    "email": self.username,
                    "targetCenter": self.club,
                    "password": self.password,
                    "_appId": "b0b88fb90e9960f706bb"
                }
            ) as response:
                result = await response.json()
                self.token = result["token"]
                self.clientId = result["clientId"]
                _LOGGER.info(result)
                _LOGGER.info(self.token)
                _LOGGER.info(self.clientId)


    async def async_get_planning(self):
        date_of_day = datetime.now().strftime("%Y-%m-%d")
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://app.heitzfit.com/c/3649/ws/api/planning/browse?startDate={date_of_day}&numberOfDays=4&idActivities=&idEmployees=&idRooms=&idGroups=&hourStart=&hourEnd=&stackBy=date&caloriesMin=&caloriesMax=&idCenter=3649",
                headers={"Authorization": f"Bearer {self.token}"}
            ) as response:
                # result_planning = await response.json()
                planning_days = await response.json()
                _LOGGER.info(type(planning_days))
                # _LOGGER.info(result_planning)
                # planning_days = json.loads(result_planning)
                # type(planning_days)
                filtered_data = filter_fields(json.dumps(planning_days))
                # print(json.dumps(filtered_data, indent=4))
                type(filtered_data)
                _LOGGER.info(filtered_data)
                return {"Planning": filtered_data}  # Adjust as needed

    async def async_get_booking(self):
        # date_of_day = datetime.now().strftime("%Y-%m-%d")
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://app.heitzfit.com/c/3649/ws/api/planning/book?idClient={self.clientId}&viewMode=0&familyActive=&familyIdClient=&familyCreatedBySelf=&include=",
                headers={"Authorization": f"Bearer {self.token}"}
            ) as response:
                result_booking = await response.json()
                # bookings = json.loads(result_booking)
                filtered_data = filter_fields(json.dumps(result_booking))
                # print(json.dumps(filtered_data, indent=4))
                _LOGGER.info(json.dumps(filtered_data))
                return {"Booking": json.dumps(filtered_data)}  # Adjust as needed

def filter_fields(data):
    fields_to_remove = {
        "idRoom", "employee", "idGroup", "idCenter", "calories", "deleted", "overlapped",
        "_roomAuthorizedToCtr", "_taskAuthorizedToCtr", "bestContrast", "_task", "_room", "_group"
    }

    def filter_dict(d):
        return {k: v for k, v in d.items() if k not in fields_to_remove}

    filtered_data = {}
    for date, activities in data.items():
        filtered_activities = []
        for activity in activities:
            filtered_activity = filter_dict(activity)
            filtered_activities.append(filtered_activity)
        filtered_data[date] = filtered_activities

    return filtered_data
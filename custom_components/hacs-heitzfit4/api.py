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
                for planning_day in planning_days:
                    for activities in planning_day:
                        try:
                            del activities["idRoom"]
                            del activities["employee"]
                            del activities["idEmployee"]
                            del activities["idGroup"]
                            del activities["idCenter"]
                            del activities["calories"]
                            del activities["deleted"]
                            del activities["overlapped"]
                            del activities["_roomAuthorizedToCtr"]
                            del activities["_taskAuthorizedToCtr"]
                            del activities["bestContrast"]
                            del activities["_task"]
                            del activities["_group"]
                            del activities["_room"]
                        except KeyError:
                            planning_days = ""
                            _LOGGER.error("Heitzfit4 : error during fetching planning data")
                _LOGGER.info(json.dump(planning_days))
                return {"Planning": json.dump(planning_days)}  # Adjust as needed

    async def async_get_booking(self):
        # date_of_day = datetime.now().strftime("%Y-%m-%d")
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://app.heitzfit.com/c/3649/ws/api/planning/book?idClient={self.clientId}&viewMode=0&familyActive=&familyIdClient=&familyCreatedBySelf=&include=",
                headers={"Authorization": f"Bearer {self.token}"}
            ) as response:
                result_booking = await response.json()
                bookings = json.loads(result_booking)
                # type(planning_days)
                for booking in bookings:
                    try:
                        del booking["qty"]
                        del booking["cancelable"]
                        del booking["queueOk"]
                        del booking["idGroup"]
                        del booking["isPaid"]
                        del booking["idCenter"]
                        del booking["partnerId"]
                        del booking["partnerIdCli"]
                        del booking["bestContrast"]
                        del booking["_teamDetail"]
                        del booking["_group"]
                        del booking["_room"]
                    except KeyError:
                        bookings = ""
                        _LOGGER.error("Heitzfit4 : error during fetching booking data")
                _LOGGER.info(json.dump(bookings))
                return {"Booking": json.dump(bookings)}  # Adjust as needed
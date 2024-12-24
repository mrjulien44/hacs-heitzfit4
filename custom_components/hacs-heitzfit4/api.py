import aiohttp
import json
# import asyncio

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
    
    async def async_get_booking(self):
        # date_of_day = datetime.now().strftime("%Y-%m-%d")
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://app.heitzfit.com/c/3649/ws/api/planning/book?idClient={self.clientId}&viewMode=0&familyActive=&familyIdClient=&familyCreatedBySelf=&include=",
                headers={"Authorization": f"Bearer {self.token}"}
            ) as response:
                result_booking = await response.json()
                _LOGGER.info(json.dumps(result_booking))
                return {json.dumps(result_booking)}  # Adjust as needed
    
    async def async_get_planning(self):
        date_of_day = datetime.now().strftime("%Y-%m-%d")
        bookings = await self.async_get_booking()
        _LOGGER.info("Récupération des bookings")
        _LOGGER.info(bookings)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://app.heitzfit.com/c/3649/ws/api/planning/browse?startDate={date_of_day}&numberOfDays=4&idActivities=&idEmployees=&idRooms=&idGroups=&hourStart=&hourEnd=&stackBy=date&caloriesMin=&caloriesMax=&idCenter=3649",
                headers={"Authorization": f"Bearer {self.token}"}
            ) as response:
                planning_days = await response.json()
                filtered_data = filter_fields(planning_days)
                _LOGGER.info("--------------")
                _LOGGER.info(type(filtered_data))
                _LOGGER.info(filtered_data)
                _LOGGER.info("--------------")
                updated_planning_data = add_booked_flag(filtered_data, bookings)
                _LOGGER.info("--- AVEC RESA -------")
                _LOGGER.info(updated_planning_data)
                
                return {"Planning": updated_planning_data}  # Adjust as needed



def add_booked_flag(planning_data, booking_data):
    booking_ids = {booking["idPlanning"] for booking in booking_data}

    for date, activities in planning_data.items():
        for activity in activities:
            if activity["idActivity"] in booking_ids:
                activity["booked"] = True

    return planning_data

def filter_fields(data):
    fields_to_remove = {
        "idRoom", "idEmployee", "idGroup", "idCenter", "calories", "deleted", "overlapped", "idActivity","manualPlaces","color",
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
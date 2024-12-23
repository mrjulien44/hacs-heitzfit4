from datetime import timedelta
import requests
import logging

from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=120)

URL = "https://app.heitzfit.com/c/3649/ws/api/planning/browse?startDate=2024-12-20&numberOfDays=6&idActivities=&idEmployees=&idRooms=&idGroups=&hourStart=&hourEnd=&stackBy=date&caloriesMin=&caloriesMax=&idCenter=3649"

def setup_platform(hass, config, add_entities, discovery_info=None):
    if discovery_info is None:
        return

    username = hass.data[DOMAIN]["username"]
    password = hass.data[DOMAIN]["password"]
    club = hass.data[DOMAIN]["club"]

    sensors = [
        Heitzfit4Sensor("heitfit4_planning", "Planning", username, password, club),
        Heitzfit4Sensor("heitfit4_reservation", "Reservations", username, password, club)
    ]
    add_entities(sensors, True)

class Heitzfit4Sensor(Entity):
    def __init__(self, name, attribute, username, password, club):
        self._name = name
        self._attribute = attribute
        self._username = username
        self._password = password
        self._club = club
        self._state = None
        self._attributes = {attribute: None}

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        return self._attributes

    @Throttle(SCAN_INTERVAL)
    def update(self):
        try:
            response = requests.get(URL, auth=(self._username, self._password))
            data = response.json()
            _LOGGER.info(data)
            self._state = data.get("state")
            self._attributes[self._attribute] = data.get(self._attribute)
        except Exception as e:
            _LOGGER.error(f"Error fetching data: {e}")
import logging
from homeassistant.components.calendar import CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.components.telegram_bot import async_send_message
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Heitzfit4 calendar based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

    await coordinator.async_config_entry_first_refresh()
    # Call the function to update the calendar
    await async_get_calendar_event_from_bookings(hass, coordinator.data["Planning"])
    async_add_entities([Heitzfit4Calendar(coordinator, config_entry)], False)

async def async_get_calendar_event_from_bookings(hass: HomeAssistant, planning_data: dict):
    calendar_component = hass.data.get(DOMAIN)
    if not calendar_component:
        calendar_component = EntityComponent(_LOGGER, DOMAIN, hass)
        hass.data[DOMAIN] = calendar_component

    calendar_entity = Heitzfit4Calendar()
    await calendar_component.async_add_entities([calendar_entity])

    await calendar_entity.async_update_events(planning_data)

class Heitzfit4Calendar(Entity):
    def __init__(self, coordinator=None, config_entry=None):
        self._events = []
        self.coordinator = coordinator
        self.config_entry = config_entry

    @property
    def name(self):
        return "Heitzfit4"

    @property
    def state(self):
        return "on"

    @property
    def extra_state_attributes(self):
        return {"events": self._events}

    async def async_update_events(self, planning_data):
        new_events = []
        for date, activities in planning_data.items():
            for activity in activities:
                if activity.get("booked"):
                    event = CalendarEvent(
                        summary=activity["activity"],
                        description=activity["activity"],
                        start=activity["start"],
                        end=activity["end"],
                        uid=str(activity["idActivity"])
                    )
                    new_events.append(event)

        # Check for events to delete
        current_uids = {event.uid for event in self._events}
        new_uids = {event.uid for event in new_events}
        events_to_delete = current_uids - new_uids

        for event in self._events:
            if event.uid in events_to_delete:
                await self.async_delete_event(event)

        self._events = new_events

    async def async_delete_event(self, event):
        self._events.remove(event)
        _LOGGER("Deleted event: %s (UID: %s)", event.summary, event.uid)
        await async_send_message(
            self.hass,
            "telegram_bot",
            f"Deleted event: {event.summary} (UID: {event.uid})"
        )
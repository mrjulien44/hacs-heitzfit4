import logging
# from homeassistant.components.calendar import CalendarEvent, CalendarEntity
# from homeassistant.core import HomeAssistant
# from homeassistant.helpers.entity_component import EntityComponent
# from homeassistant.helpers.entity import Entity
# from homeassistant.helpers.event import async_track_time_interval
# from homeassistant.config_entries import ConfigEntry
# from homeassistant.helpers.entity_platform import AddEntitiesCallback

# from .const import DOMAIN

# _LOGGER = logging.getLogger(__name__)


# async def async_setup_entry(
#     hass: HomeAssistant,
#     config_entry: ConfigEntry,
#     async_add_entities: AddEntitiesCallback,
# ) -> None:
#     """Set up Heitzfit4 calendar based on a config entry."""
#     # coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
#     coordinator = hass.data[DOMAIN][config_entry.entry_id]

#     # calendars = config_entry["calendars"]

#     await coordinator.async_config_entry_first_refresh()
#     # Call the function to update the calendar
#     _LOGGER.info("CALENDAR ASYNC SETUP ENTRY coordinator.data")
#     _LOGGER.info(coordinator.data["Planning"])
#     await async_get_calendar_event_from_bookings(hass, coordinator.data["Planning"])
#     async_add_entities([Heitzfit4Calendar(coordinator, config_entry)], False)



# async def async_get_calendar_event_from_bookings(hass: HomeAssistant, planning_data: dict, async_add_entities: AddEntitiesCallback):
#     calendar_component = hass.data.get(DOMAIN)
#     _LOGGER.info("CALENDAR async_get_calendar_event_from_bookings 1")
#     _LOGGER.info(calendar_component)
#     if not calendar_component:
#         _LOGGER.info("CALENDAR async_get_calendar_event_from_bookings NOT IN CALENDAR")
#         calendar_component = EntityComponent(_LOGGER, DOMAIN, hass)
#         hass.data[DOMAIN] = calendar_component

#     # Check if the calendar entity already exists
#     # calendar_entity = next(
#     #     (entity for entity in calendar_component.entities if entity.name == "Heitzfit4"), 
#     #     None
#     # )

#     # if not calendar_entity:
#     #     calendar_entity = Heitzfit4Calendar()
#     #     await calendar_component.async_add_entities([calendar_entity])

#     # await calendar_entity.async_update_events(planning_data)

#     calendar_entity = Heitzfit4Calendar()
#     _LOGGER.info("CALENDAR async_get_calendar_event_from_bookings calendar_entity")
#     _LOGGER.info(calendar_entity)
#     async_add_entities([calendar_entity])
#     await calendar_entity.async_update_events(planning_data)



# class Heitzfit4Calendar(Entity, CalendarEntity):
#     _LOGGER.info("CALENDAR Heitzfit4Calendar")
#     def __init__(self, coordinator=None, config_entry=None):
#         self._events = []
#         self.coordinator = coordinator
#         self.config_entry = config_entry

#     @property
#     def name(self):
#         return "Heitzfit4"

#     @property
#     def state(self):
#         return "on"

#     @property
#     def extra_state_attributes(self):
#         return {"events": self._events}

#     async def async_update_events(self, planning_data):
#         _LOGGER.info("CALENDAR async_update_events")
#         new_events = []
#         for date, activities in planning_data.items():
#             for activity in activities:
#                 if activity.get("booked"):
#                     event = CalendarEvent(
#                         summary=activity["activity"],
#                         description=activity["activity"],
#                         start=activity["start"],
#                         end=activity["end"],
#                         uid=str(activity["idActivity"])
#                     )
#                     new_events.append(event)
#                     _LOGGER.info("New event: %s (UID: %s)", event.summary, event.uid)

#         # Check for events to delete
#         current_uids = {event.uid for event in self._events}
#         new_uids = {event.uid for event in new_events}
#         events_to_delete = current_uids - new_uids

#         for event in self._events:
#             if event.uid in events_to_delete:
#                 await self.async_delete_event(event)

#         self._events = new_events

#     async def async_delete_event(self, event):
#         self._events.remove(event)
#         _LOGGER.info("Deleted event: %s (UID: %s)", event.summary, event.uid)
#         # await async_send_message(
#         #     self.hass,
#         #     "telegram_bot",
#         #     f"Deleted event: {event.summary} (UID: {event.uid})"
#         # )







#  NEW VERSION


import asyncio
from typing import Any
from ical.calendar import Calendar
from ical.calendar_stream import IcsCalendarStream
from ical.event import Event
from ical.exceptions import CalendarParseError
from ical.store import EventStore, EventStoreError
from ical.types import Range, Recur

from datetime import datetime
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.components.calendar import CalendarEntity, CalendarEntityFeature, CalendarEvent
from homeassistant.util.dt import get_time_zone
from homeassistant.util import dt as dt_util
from homeassistant.exceptions import HomeAssistantError
from zoneinfo import ZoneInfo

from homeassistant.helpers.update_coordinator import CoordinatorEntity
# from .init import Heitzfit4DataUpdateCoordinator

from .const import DOMAIN
from .store import LocalCalendarStore
PRODID = "-//homeassistant.io//heitzfit4 1.0//EN"

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    """Set up the local calendar platform."""
    ics = await coordinator.async_load()
    calendar: Calendar = await hass.async_add_executor_job(
        IcsCalendarStream.calendar_from_ics, ics
    )
    calendar.prodid = PRODID

    """Set up ReCollect Waste sensors based on a config entry."""
    
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([Heitzfit4Calendar(coordinator, config_entry)], False)


@callback
def async_get_calendar_event_from_bookings(planning_data, timezone) -> CalendarEvent:
    """Get a HASS CalendarEvent from a Pronote Lesson."""
    tz = ZoneInfo(timezone)
    activity = planning_data
    _LOGGER.info(activity)      
    return CalendarEvent(
        summary=f"{activity["activity"]} ({activity["duration"]})",
        description=f"{activity["activity"]} - {activity["room"]} ({activity["duration"]})",
        start=activity["start"],
        end=activity["end"],
        uid=str(activity["idActivity"])
    )

class Heitzfit4Calendar(CoordinatorEntity, CalendarEntity):

    _attr_supported_features = (
        CalendarEntityFeature.DELETE_EVENT
        | CalendarEntityFeature.UPDATE_EVENT
    )

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        entry: ConfigEntry,
        store: LocalCalendarStore,
    ) -> None:
        """Initialize the ReCollect Waste entity."""
        super().__init__(coordinator, entry)

        calendar_name = "Heitzfit4"
        self._store = coordinator
        self._attr_unique_id = "Heitzfit4_calendar"
        self._attr_name = f"Reservation {calendar_name}"
        self._attr_device_info = DeviceInfo(
            name="Heitzfit4",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={
                (DOMAIN, "Heitzfit4")
            },
            manufacturer="Heitzfit4",
            model="Heitzfit4"
        )
        self._calendar_lock = asyncio.Lock()
        self._event: CalendarEvent | None = None
    
    @property
    def icon(self) -> str | None:
        """Return the icon of the sensor."""
        return "mdi:weight-lifter"
    
    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        return self._event

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.info("CALENDAR _handle_coordinator_update")
        # try:
        #     bookings = self.coordinator.data["planning"]
        #     if bookings is None:
        #         return None

        #     now = datetime.now()
        #     current_event = next(
        #         event for event in bookings if event.start >= now and now < event.end
        #     )
        # except StopIteration:
        #     self._event = None
        # else:
        #     self._event = async_get_calendar_event_from_bookings(
        #         current_event, self.hass.config.time_zone
        #     )

        # super()._handle_coordinator_update()

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        new_events=[]
        for date, activities in self.coordinator.data["Planning"].items():
            for activity in activities:
                if activity.get("booked"):
                    new_events.append(activity)
        return [
            # async_get_calendar_event_from_bookings(self.coordinator.data["Planning"], hass.config.time_zone)
            async_get_calendar_event_from_bookings(event, hass.config.time_zone)
            # for event in self.coordinator.data["planning"]
            for event in new_events

        ]
    

    # async def async_update(self) -> None:
    #     """Update entity state with the next upcoming event."""
    #     now = dt_util.now()
    #     events = self._calendar.timeline_tz(now.tzinfo).active_after(now)
    #     if event := next(events, None):
    #         self._event = _get_calendar_event(event)
    #     else:
    #         self._event = None

    async def _async_store(self) -> None:
        """Persist the calendar to disk."""
        content = IcsCalendarStream.calendar_to_ics(self._calendar)
        await self._store.async_store(content)

    # async def async_create_event(self, **kwargs: Any) -> None:
    #     """Add a new event to calendar."""
    #     event = _parse_event(kwargs)
    #     async with self._calendar_lock:
    #         event_store = EventStore(self._calendar)
    #         await self.hass.async_add_executor_job(event_store.add, event)
    #         await self._async_store()
    #     await self.async_update_ha_state(force_refresh=True)

    async def async_delete_event(
        self,
        uid: str,
        recurrence_id: str | None = None,
        recurrence_range: str | None = None,
    ) -> None:
        """Delete an event on the calendar."""
        range_value: Range = Range.NONE
        if recurrence_range == Range.THIS_AND_FUTURE:
            range_value = Range.THIS_AND_FUTURE
        async with self._calendar_lock:
            try:
                EventStore(self._calendar).delete(
                    uid,
                    recurrence_id=recurrence_id,
                    recurrence_range=range_value,
                )
            except EventStoreError as err:
                raise HomeAssistantError(f"Error while deleting event: {err}") from err
            await self._async_store()
        await self.async_update_ha_state(force_refresh=True)

    async def async_update_event(
        self,
        uid: str,
        event: dict[str, Any],
        recurrence_id: str | None = None,
        recurrence_range: str | None = None,
    ) -> None:
        """Update an existing event on the calendar."""
        new_event = _parse_event(event)
        range_value: Range = Range.NONE
        if recurrence_range == Range.THIS_AND_FUTURE:
            range_value = Range.THIS_AND_FUTURE

        async with self._calendar_lock:
            event_store = EventStore(self._calendar)

            def apply_edit() -> None:
                event_store.edit(
                    uid,
                    new_event,
                    recurrence_id=recurrence_id,
                    recurrence_range=range_value,
                )

            try:
                await self.hass.async_add_executor_job(apply_edit)
            except EventStoreError as err:
                raise HomeAssistantError(f"Error while updating event: {err}") from err
            await self._async_store()
        await self.async_update_ha_state(force_refresh=True)



def _parse_event(event: dict[str, Any]) -> Event:
    """Parse an ical event from a home assistant event dictionary."""
    if rrule := event.get(EVENT_RRULE):
        event[EVENT_RRULE] = Recur.from_rrule(rrule)

    # This function is called with new events created in the local timezone,
    # however ical library does not properly return recurrence_ids for
    # start dates with a timezone. For now, ensure any datetime is stored as a
    # floating local time to ensure we still apply proper local timezone rules.
    # This can be removed when ical is updated with a new recurrence_id format
    # https://github.com/home-assistant/core/issues/87759
    for key in (EVENT_START, EVENT_END):
        if (
            (value := event[key])
            and isinstance(value, datetime)
            and value.tzinfo is not None
        ):
            event[key] = dt_util.as_local(value).replace(tzinfo=None)

    try:
        return Event(**event)
    except CalendarParseError as err:
        _LOGGER.debug("Error parsing event input fields: %s (%s)", event, str(err))
        raise vol.Invalid("Error parsing event input fields") from err
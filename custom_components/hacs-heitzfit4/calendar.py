import logging
from datetime import datetime
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.util.dt import get_time_zone
from zoneinfo import ZoneInfo

from homeassistant.helpers.update_coordinator import CoordinatorEntity
# from .init import Heitzfit4DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ReCollect Waste sensors based on a config entry."""
    # coordinator: Heitzfit4DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([Heitzfit4Calendar(coordinator, config_entry)], False)


@callback
def async_get_calendar_event_from_bookings(planning_data, timezone) -> CalendarEvent:
    """Get a HASS CalendarEvent from Heitzfit4 booking."""
    tz = ZoneInfo(timezone)
    activity = planning_data
    return CalendarEvent(
        summary=f"{activity["activity"]}",
        description=f"{activity["activity"]} - {activity["room"]} ({activity["duration"]})",
        start=activity["start"],
        end=activity["end"],
        uid=str(activity["idActivity"])
    )

class Heitzfit4Calendar(CoordinatorEntity, CalendarEntity):

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the ReCollect Waste entity."""
        super().__init__(coordinator, entry)

        calendar_name = "Heitzfit4"
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
            async_get_calendar_event_from_bookings(event, hass.config.time_zone)
            for event in new_events
        ]
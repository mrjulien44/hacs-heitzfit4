from datetime import datetime
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.util.dt import get_time_zone
from zoneinfo import ZoneInfo

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import heitzfit4DataUpdateCoordinator
from .heitzfit4_formatter import format_displayed_activity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ReCollect Waste sensors based on a config entry."""
    coordinator: heitzfit4DataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]["coordinator"]

    await coordinator.async_config_entry_first_refresh()

    async_add_entities([heitzfit4Calendar(coordinator, config_entry)], False)


@callback
def async_get_calendar_event_from_activitys(activity, timezone) -> CalendarEvent:
    """Get a HASS CalendarEvent from a heitzfit4 activity."""
    tz = ZoneInfo(timezone)

    activity_name = format_displayed_activity(activity)
     if activity.deleted:
         activity_name = f"Annulé - {activity_name}"

    return CalendarEvent(
        summary=activity_name,
        # description=f"{activity.teacher_name} - Salle {activity.classroom}",
        # location=f"Salle {activity.classroom}",
        start=activity.start.replace(tzinfo=tz),
        end=activity.end.replace(tzinfo=tz),
    )


class heitzfit4Calendar(CoordinatorEntity, CalendarEntity):

    def __init__(
        self,
        coordinator: heitzfit4DataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the ReCollect Waste entity."""
        super().__init__(coordinator, entry)

        child_info = coordinator.data["child_info"]
        calendar_name = "sport"
        # calendar_name = child_info.name
        # nickname = self.coordinator.config_entry.options.get("nickname", "")
        # if nickname != "":
        #     calendar_name = nickname

        self._attr_translation_key = "timetable"
        # self._attr_translation_placeholders = {"child": calendar_name}
        self._attr_unique_id = f"{coordinator.data['sensor_prefix']}-timetable"
        self._attr_name = f"Planning de {calendar_name}"
        self._attr_device_info = DeviceInfo(
            name=f"heitzfit4 - {self.coordinator.data.name}",
            # name=f"heitzfit4 - {self.coordinator.data['child_info'].name}",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={
                (DOMAIN, f"heitzfit4 - {self.coordinator.data.name}")
                # (DOMAIN, f"heitzfit4 - {self.coordinator.data['child_info'].name}")
            },
            manufacturer="heitzfit4",
            model=self.coordinator.data.name,
            # model=self.coordinator.data["child_info"].name,
        )
        self._event: CalendarEvent | None = None

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        return self._event

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        try:
            activitys = self.coordinator.data["activitys_period"]
            if activitys is None:
                return None

            now = datetime.now()
            current_event = next(
                event for event in activitys if event.start >= now and now < event.end
            )
        except StopIteration:
            self._event = None
        else:
            self._event = async_get_calendar_event_from_activitys(
                current_event, self.hass.config.time_zone
            )

        super()._handle_coordinator_update()

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        return [
            async_get_calendar_event_from_activitys(event, hass.config.time_zone)
            for event in filter(
                lambda activity: activity.canceled == False,
                self.coordinator.data["activitys_period"],
            )
        ]

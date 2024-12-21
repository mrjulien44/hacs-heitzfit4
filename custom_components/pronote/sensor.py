from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from datetime import datetime

from .coordinator import heitzfit4DataUpdateCoordinator
from .heitzfit4_formatter import *

from .const import (
    DOMAIN,
    # GRADES_TO_DISPLAY,
    # EVALUATIONS_TO_DISPLAY,
    # DEFAULT_LUNCH_BREAK_TIME,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: heitzfit4DataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]["coordinator"]

    sensors = [
        heitzfit4ChildSensor(coordinator),
        heitzfit4TimetableSensor(coordinator, "today"),
        heitzfit4TimetableSensor(coordinator, "tomorrow"),
        heitzfit4TimetableSensor(coordinator, "next_day"),
        heitzfit4TimetableSensor(coordinator, "period"),
        # heitzfit4GradesSensor(coordinator),
        heitzfit4reservationSensor(coordinator, ""),
        heitzfit4reservationSensor(coordinator, "_period"),
        # heitzfit4AbsensesSensor(coordinator),
        # heitzfit4EvaluationsSensor(coordinator),
        # heitzfit4AveragesSensor(coordinator),
        # heitzfit4PunishmentsSensor(coordinator),
        # heitzfit4DelaysSensor(coordinator),
        # heitzfit4InformationAndSurveysSensor(coordinator),
        heitzfit4GenericSensor(coordinator, "ical_url", "timetable_ical_url"),
        heitzfit4GenericSensor(
            coordinator, "next_alarm", "next_alarm", None, SensorDeviceClass.TIMESTAMP
        ),
        heitzfit4MenusSensor(coordinator),
    ]

    async_add_entities(sensors, False)


class heitzfit4ChildSensor(CoordinatorEntity, SensorEntity):
    """Representation of a heitzfit4 sensor."""

    def __init__(self, coordinator) -> None:
        """Initialize the heitzfit4 sensor."""
        super().__init__(coordinator)
        # self._child_info = coordinator.data["child_info"]
        # self._account_type = coordinator.data["account_type"]
        self._attr_unique_id = (
            f"heitzfit4-{self.coordinator.data['sensor_prefix']}-identity"
        )
        self._attr_device_info = DeviceInfo(
            # name=f"heitzfit4 - {self.coordinator.data['child_info'].name}",
            name=f"heitzfit4 - {self.coordinator.data.name}",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={
                # (DOMAIN, f"heitzfit4 - {self.coordinator.data['child_info'].name}")
                (DOMAIN, f"heitzfit4 - {self.coordinator.data.name}")
            },
            manufacturer="heitzfit4",
            model=self.coordinator.data.name,
            # model=self.coordinator.data["child_info"].name,
        )

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DOMAIN}_{self.coordinator.data['sensor_prefix']}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.name
        # return self._child_info.name

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            # "full_name": self._child_info.name,
            # "nickname": self.coordinator.config_entry.options.get("nickname"),
            # "class_name": self._child_info.class_name,
            # "establishment": self._child_info.establishment,
            # "via_parent_account": self._account_type == "parent",
            "club": self.coordinator.config_entry.options.get("club"),
            "updated_at": self.coordinator.last_update_success_time,
        }


class heitzfit4GenericSensor(CoordinatorEntity, SensorEntity):
    """Representation of a heitzfit4 sensor."""

    def __init__(
        self,
        coordinator,
        coordinator_key: str,
        name: str,
        state: str = None,
        device_class: str = None,
    ) -> None:
        """Initialize the heitzfit4 sensor."""
        super().__init__(coordinator)
        self._coordinator_key = coordinator_key
        self._name = name
        self._state = state
        self._attr_unique_id = (
            f"heitzfit4-{self.coordinator.data['sensor_prefix']}-{self._name}"
        )
        self._attr_device_info = DeviceInfo(
            name=f"heitzfit4 - {self.coordinator.data.name}",
            # name=f"heitzfit4 - {self.coordinator.data['child_info'].name}",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={
                # (DOMAIN, f"heitzfit4 - {self.coordinator.data['child_info'].name}")
                (DOMAIN, f"heitzfit4 - {self.coordinator.data.name}")
            },
            manufacturer="heitzfit4",
            model=self.coordinator.data.name,
            # model=self.coordinator.data["child_info"].name,
        )
        if device_class is not None:
            self._attr_device_class = device_class

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DOMAIN}_{self.coordinator.data['sensor_prefix']}_{self._name}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data[self._coordinator_key] is None:
            return "unavailable"
        elif self._state == "len":
            return len(self.coordinator.data[self._coordinator_key])
        elif self._state is not None:
            return self._state
        else:
            return self.coordinator.data[self._coordinator_key]

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {"updated_at": self.coordinator.last_update_success_time}

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data[self._coordinator_key] is not None
        )


class heitzfit4TimetableSensor(heitzfit4GenericSensor):
    """Representation of a heitzfit4 sensor."""

    def __init__(self, coordinator: heitzfit4DataUpdateCoordinator, suffix: str) -> None:
        """Initialize the heitzfit4 sensor."""
        super().__init__(coordinator, "activitys_" + suffix, "timetable_" + suffix, "len")
        self._suffix = suffix
        self._activitys = []
        self._start_at = None
        self._end_at = None
        # self._lunch_break_start_at = None
        # self._lunch_break_end_at = None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        self._activitys = self.coordinator.data["activitys_" + self._suffix]
        attributes = []
        canceled_counter = None
        single_day = self._suffix in ["today", "tomorrow", "next_day"]
        # lunch_break_time = datetime.strptime(
        #     self.coordinator.config_entry.options.get(
        #         "lunch_break_time", DEFAULT_LUNCH_BREAK_TIME
        #     ),
        #     "%H:%M",
        # ).time()

        if self._activitys is not None:
            self._start_at = None
            self._end_at = None
            # self._lunch_break_start_at = None
            # self._lunch_break_end_at = None
            canceled_counter = 0
            for activity in self._activitys:
                index = self._activitys.index(activity)
                if not (
                    activity.start == self._activitys[index - 1].start
                    and activity.canceled is True
                ):
                    attributes.append(format_activity(activity, lunch_break_time))
                if activity.canceled is False and self._start_at is None:
                    self._start_at = activity.start
                if activity.canceled is True:
                    canceled_counter += 1
                if single_day is True and activity.canceled is False:
                    self._end_at = activity.end
                    # if activity.end.time() < lunch_break_time:
                    #     self._lunch_break_start_at = activity.end
                    # if (
                    #     self._lunch_break_end_at is None
                    #     and activity.start.time() >= lunch_break_time
                    # ):
                    #     self._lunch_break_end_at = activity.start
            self._activitys = []

        result = {
            "updated_at": self.coordinator.last_update_success_time,
            "activitys": attributes,
            "canceled_activitys_counter": canceled_counter,
            "day_start_at": self._start_at,
            "day_end_at": self._end_at,
        }

        # if single_day is True:
        #     result["lunch_break_start_at"] = self._lunch_break_start_at
        #     result["lunch_break_end_at"] = self._lunch_break_end_at

        return result


# class heitzfit4GradesSensor(heitzfit4GenericSensor):
#     """Representation of a heitzfit4 sensor."""

#     def __init__(self, coordinator: heitzfit4DataUpdateCoordinator) -> None:
#         """Initialize the heitzfit4 sensor."""
#         super().__init__(coordinator, "grades", "grades", "len")

#     @property
#     def extra_state_attributes(self):
#         """Return the state attributes."""
#         attributes = []
#         index_note = 0
#         if self.coordinator.data["grades"] is not None:
#             for grade in self.coordinator.data["grades"]:
#                 index_note += 1
#                 if index_note == GRADES_TO_DISPLAY:
#                     break
#                 attributes.append(format_grade(grade))

#         return {
#             "updated_at": self.coordinator.last_update_success_time,
#             "grades": attributes,
#         }


class heitzfit4reservationSensor(heitzfit4GenericSensor):
    """Representation of a heitzfit4 sensor."""

    def __init__(self, coordinator: heitzfit4DataUpdateCoordinator, suffix: str) -> None:
        """Initialize the heitzfit4 sensor."""
        super().__init__(coordinator, "reservation" + suffix, "reservation" + suffix, "len")
        self._suffix = suffix

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attributes = []
        todo_counter = None
        if self.coordinator.data[f"reservation{self._suffix}"] is not None:
            todo_counter = 0
            for reservation in self.coordinator.data[f"reservation{self._suffix}"]:
                attributes.append(format_reservation(reservation))
                if reservation.done is False:
                    todo_counter += 1

        return {
            "updated_at": self.coordinator.last_update_success_time,
            "reservation": attributes,
            "todo_counter": todo_counter,
        }


# class heitzfit4AbsensesSensor(heitzfit4GenericSensor):
#     """Representation of a heitzfit4 sensor."""

#     def __init__(self, coordinator) -> None:
#         """Initialize the heitzfit4 sensor."""
#         super().__init__(coordinator, "absences", "absences", "len")

#     @property
#     def extra_state_attributes(self):
#         """Return the state attributes."""
#         attributes = []
#         if self.coordinator.data["absences"] is not None:
#             for absence in self.coordinator.data["absences"]:
#                 attributes.append(format_absence(absence))

#         return {
#             "updated_at": self.coordinator.last_update_success_time,
#             "absences": attributes,
#         }


# class heitzfit4DelaysSensor(heitzfit4GenericSensor):
#     """Representation of a heitzfit4 sensor."""

#     def __init__(self, coordinator) -> None:
#         """Initialize the heitzfit4 sensor."""
#         super().__init__(coordinator, "delays", "delays", "len")

#     @property
#     def extra_state_attributes(self):
#         """Return the state attributes."""
#         attributes = []
#         if self.coordinator.data["delays"] is not None:
#             for delay in self.coordinator.data["delays"]:
#                 attributes.append(format_delay(delay))

#         return {
#             "updated_at": self.coordinator.last_update_success_time,
#             "delays": attributes,
#         }


# class heitzfit4EvaluationsSensor(heitzfit4GenericSensor):
#     """Representation of a heitzfit4 sensor."""

#     def __init__(self, coordinator) -> None:
#         """Initialize the heitzfit4 sensor."""
#         super().__init__(coordinator, "evaluations", "evaluations", "len")

#     @property
#     def extra_state_attributes(self):
#         """Return the state attributes."""
#         attributes = []
#         index_note = 0
#         if self.coordinator.data["evaluations"] is not None:
#             for evaluation in self.coordinator.data["evaluations"]:
#                 index_note += 1
#                 if index_note == EVALUATIONS_TO_DISPLAY:
#                     break
#                 attributes.append(format_evaluation(evaluation))

#         return {
#             "updated_at": self.coordinator.last_update_success_time,
#             "evaluations": attributes,
#         }


# class heitzfit4AveragesSensor(heitzfit4GenericSensor):
#     """Representation of a heitzfit4 sensor."""

#     def __init__(self, coordinator) -> None:
#         """Initialize the heitzfit4 sensor."""
#         super().__init__(coordinator, "averages", "averages", "len")

#     @property
#     def extra_state_attributes(self):
#         """Return the state attributes."""
#         attributes = []
#         if self.coordinator.data["averages"] is not None:
#             for average in self.coordinator.data["averages"]:
#                 attributes.append(format_average(average))
#         return {
#             "updated_at": self.coordinator.last_update_success_time,
#             "averages": attributes,
#         }


# class heitzfit4PunishmentsSensor(heitzfit4GenericSensor):
#     """Representation of a heitzfit4 sensor."""

#     def __init__(self, coordinator) -> None:
#         """Initialize the heitzfit4 sensor."""
#         super().__init__(coordinator, "punishments", "punishments", "len")

#     @property
#     def extra_state_attributes(self):
#         """Return the state attributes."""
#         attributes = []
#         if self.coordinator.data["punishments"] is not None:
#             for punishment in self.coordinator.data["punishments"]:
#                 attributes.append(format_punishment(punishment))
#         return {
#             "updated_at": self.coordinator.last_update_success_time,
#             "punishments": attributes,
#         }


# class heitzfit4MenusSensor(heitzfit4GenericSensor):
#     """Representation of a heitzfit4 sensor."""

#     def __init__(self, coordinator) -> None:
#         """Initialize the heitzfit4 sensor."""
#         super().__init__(coordinator, "menus", "menus", "len")

#     @property
#     def extra_state_attributes(self):
#         """Return the state attributes."""
#         attributes = []
#         if self.coordinator.data["menus"] is not None:
#             for menu in self.coordinator.data["menus"]:
#                 attributes.append(format_menu(menu))
#         return {
#             "updated_at": self.coordinator.last_update_success_time,
#             "menus": attributes,
#         }


# class heitzfit4InformationAndSurveysSensor(heitzfit4GenericSensor):
#     """Representation of a heitzfit4 sensor."""

#     def __init__(self, coordinator) -> None:
#         """Initialize the heitzfit4 sensor."""
#         super().__init__(
#             coordinator, "information_and_surveys", "information_and_surveys", "len"
#         )

#     @property
#     def extra_state_attributes(self):
#         """Return the state attributes."""
#         attributes = []
#         unread_count = None
#         if not self.coordinator.data["information_and_surveys"] is None:
#             unread_count = 0
#             for information_and_survey in self.coordinator.data[
#                 "information_and_surveys"
#             ]:
#                 attributes.append(format_information_and_survey(information_and_survey))
#                 if information_and_survey.read is False:
#                     unread_count += 1
#         return {
#             "updated_at": self.coordinator.last_update_success_time,
#             "unread_count": unread_count,
#             "information_and_surveys": attributes,
#         }

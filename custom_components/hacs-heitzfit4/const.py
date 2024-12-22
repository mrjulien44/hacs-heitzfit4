"""Constants for the heitzfit4 integration."""

from homeassistant.const import Platform

DOMAIN = "hacs-heitzfit4"
EVENT_TYPE = "heitzfit4_event"

LESSON_MAX_DAYS = 6
RESERVATION_MAX_DAYS = 6
RESERVATION_DESC_MAX_LENGTH = 125
DEFAULT_REFRESH_INTERVAL = 15
DEFAULT_ALARM_OFFSET = 60

PLATFORMS = [Platform.SENSOR, Platform.CALENDAR]

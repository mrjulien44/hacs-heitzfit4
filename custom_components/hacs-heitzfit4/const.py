"""Constants for the heitzfit4 integration."""

from homeassistant.const import Platform

DOMAIN = "hacs-heitzfit4"
EVENT_TYPE = "heitzfit4_event"

LESSON_MAX_DAYS = 6
# LESSON_NEXT_DAY_SEARCH_LIMIT = 30
RESERVATION_MAX_DAYS = 6

# GRADES_TO_DISPLAY = 11
# EVALUATIONS_TO_DISPLAY = 15

# INFO_SURVEY_LIMIT_MAX_DAYS = 7

RESERVATION_DESC_MAX_LENGTH = 125

# default values for options
DEFAULT_REFRESH_INTERVAL = 15
DEFAULT_ALARM_OFFSET = 60
# DEFAULT_LUNCH_BREAK_TIME = "13:00"

PLATFORMS = [Platform.SENSOR, Platform.CALENDAR]

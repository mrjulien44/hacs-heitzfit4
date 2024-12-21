# heitzfit4 integration for Home Assistant

## Installation

### Using HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=delphiki&repository=hass-heitzfit4&category=integration)

OR

If you can't find the integration, add this repository to HACS, then:  
HACS > Integrations > **heitzfit4**

### Manual install

Copy the `heitzfit4` folder from latest release to the `custom_components` folder in your `config` folder.

## Configuration

Click on the following button:  
[![Open your Home Assistant instance and start setting up a new integration of a specific brand.](https://my.home-assistant.io/badges/brand.svg)](https://my.home-assistant.io/redirect/brand/?brand=heitzfit4)  

Or go to :  
Settings > Devices & Sevices > Integrations > Add Integration, and search for "heitzfit4"

You can choose between two options when adding a config entry.  

### using username and password

Use your heitzfit4 URL with username, password and ENT (optional):  
![heitzfit4 config flow](doc/config_flow_username_password.png)

## Usage

This integration provides several sensors, always prefixed with `heitzfit4_LASTNAME_FIRSTNAME` (where `LASTNAME` and `FIRSTNAME` are replaced), for example `sensor.heitzfit4_LASTNAME_FIRSTNAME_timetable_today`.


| Sensor | Description |
|--------|-------------|
| `sensor.heitzfit4_LASTNAME_FIRSTNAME` | basic informations about your child |
| `[...]_timetable_today` | today's timetable |
| `[...]_timetable_tomorrow` | tomorrow's timetable |
| `[...]_timetable_next_day` | next school day timetable |
| `[...]_timetable_period` | timetable for next 15 days |
| `[...]_timetable_ical_url` | iCal URL for the timetable (if available) |
| `[...]_reservation` | reservation |
| `[...]_reservation_period` | reservation for max 6 days |

The sensors are updated every 15 minutes.

## Cards

Cards are available here: https://github.com/delphiki/lovelace-heitzfit4

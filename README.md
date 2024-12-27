# heitzfit4 integration for Home Assistant
![heitzfit4 logo](doc/logo_heitzfit4.png)
## Installation

### Using HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mrjulien44s&repository=hacs-heitzfit4&category=integration)

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

Use your heitzfit4 with username, password and Club Id:  
![heitzfit4 config flow](doc/config_flow_username_password.png)

## Usage


| Sensor | Description |
|--------|-------------|
| `sensor.heitzfit4_planning` | Planning for coming days |


The sensors are updated every 120 minutes.

## Cards

Use a markdown card for now

Sample for planning

```
{%- set days = state_attr('sensor.heitzfit4_planning', 'planning') -%} {%- for day in days -%}
  <h2><ha-icon icon="mdi:calendar-today"></ha-icon> {{as_timestamp(day) | timestamp_custom('%d %b') + ' (' + as_timestamp(day) | timestamp_custom('%A') + ')'}}</h2>
  {%- for activities in days[day] -%}
    {%- set places = activities.placesTaken | string + "/" + activities.placesMax | string -%}
    {%- set booking = "info" -%}
    {%- if activities.booked %}
      {%- set booking = "success" -%}
    {%- endif -%}
      <ha-alert title="{{as_timestamp(activities.start) | timestamp_custom('%R') + '&nbsp;&nbsp;' + activities.activity + '&nbsp;&nbsp;(' + places + ')'}}" alert-type="{{booking}}">{{'&nbsp;&nbsp;&nbsp;@&nbsp;' + activities.room}}</ha-alert>
  {%- endfor -%}
{%- endfor -%}
```
![heitzfit4 planning detail](doc/planning.png)

Sample for booking

```
{%- set days = state_attr('sensor.heitzfit4_planning', 'planning') -%} {%- for day in days -%}
  <h2><ha-icon icon="mdi:calendar-today"></ha-icon> {{as_timestamp(day) | timestamp_custom('%d %b')}}{{' (' + as_timestamp(day) | timestamp_custom('%A') + ')'}}</h2>
  {%- for activities in days[day] -%}
    {%- set places = activities.placesTaken | string + "/" + activities.placesMax | string -%}
    {%- set booking = "info" -%}
    {%- if activities.booked %}
      {%- set booking = "success" -%}
      <ha-alert title="{{as_timestamp(activities.start) | timestamp_custom('%R') + '&nbsp;&nbsp;' + activities.activity + '&nbsp;&nbsp;(' + places + ')'}}" alert-type="{{booking}}">{{'&nbsp;&nbsp;&nbsp;@&nbsp;' + activities.room}}</ha-alert>
    {%- endif -%}
  {%- endfor -%}
{%- endfor -%}
```
![heitzfit4 planning detail](doc/booking.png)

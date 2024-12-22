from homeassistant.helpers import discovery
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

DOMAIN = "hacs-heitzfit4"

def setup(hass, config):
    conf = config[DOMAIN]
    username = conf[CONF_USERNAME]
    password = conf[CONF_PASSWORD]
    club = conf["club"]

    hass.data[DOMAIN] = {
        "username": username,
        "password": password,
        "club": club
    }

    discovery.load_platform(hass, "sensor", DOMAIN, {}, config)
    return True
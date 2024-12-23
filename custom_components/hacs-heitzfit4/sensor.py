from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Heitzfit4 sensor entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        Heitzfit4Sensor(coordinator, "heitfit4_planning", "Planning"),
        Heitzfit4Sensor(coordinator, "heitfit4_booking", "booking")
    ])

class Heitzfit4Sensor(CoordinatorEntity, SensorEntity):
    """Representation of a Heitzfit4 sensor."""

    def __init__(self, coordinator, name, attribute):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = name
        self._attribute = attribute

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._attribute)

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {self._attribute: self.coordinator.data.get(self._attribute)}
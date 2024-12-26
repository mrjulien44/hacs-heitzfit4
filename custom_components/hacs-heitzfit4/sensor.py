from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Heitzfit4 sensor entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        Heitzfit4Sensor(coordinator, "heitzfit4_planning", "planning")
        # Heitzfit4Sensor(coordinator, "heitzfit4_booking", "booking")
    ], True)

class Heitzfit4Sensor(CoordinatorEntity, SensorEntity):
    """Representation of a Heitzfit4 sensor."""

    def __init__(self, coordinator, name, attribute):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = name
        self._attribute = attribute
        self._attr_native_value = 6
        """Initisalisation de notre entité"""
        self._attr_has_entity_name = True
        self._attr_name = "Heitzfit4"
        self._attr_unique_id = "Heitzfit4"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
    
    @property
    def icon(self) -> str | None:
        """Return the icon of the sensor."""
        return "mdi:WeightLifter"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._attribute)
    
    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "planning": self.coordinator.data.get("Planning")
        }
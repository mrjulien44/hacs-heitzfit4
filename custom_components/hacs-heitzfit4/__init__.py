"""Initialisation du package de l'intégration """
import asyncio
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .api import Heitzfit4API
from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry
):  # pylint: disable=unused-argument
    """Initialisation de l'intégration"""
    # _LOGGER.info(
    #     "Initializing %s integration with plaforms: %s with config: %s",
    #     DOMAIN,
    #     PLATFORMS,
    #     config,
    # )
    coordinator = Heitzfit4DataUpdateCoordinator(hass, config)
    await coordinator.async_config_entry_first_refresh()
    _LOGGER.info("Coordinator initialized")
    _LOGGER.info(coordinator)
    hass.data.setdefault(DOMAIN, {})[config.entry_id] = coordinator

    for platform in PLATFORMS:
        hass.async_add_job(
            hass.config_entries.async_forward_entry_setup(config, platform)
        )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

class Heitzfit4DataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Heitzfit4 data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize."""
        self.hass = hass
        self.entry = entry
        self.api = Heitzfit4API(entry.data["club"], entry.data["username"], entry.data["password"], entry.data["nbDays"])
        # self._attr_name = entry.get("name")
        # self._attr_unique_id = entry.get("entity_id")
        self._attr_has_entity_name = True

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=120),
        )

    async def _async_update_data(self):
        """Update data via library."""
        await self.api.async_sign_in()
        # await self.api.async_get_planning()
        return await self.api.async_get_planning()
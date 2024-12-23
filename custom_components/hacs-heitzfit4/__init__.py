"""Initialisation du package de l'intégration """
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry
):  # pylint: disable=unused-argument
    """Initialisation de l'intégration"""
    _LOGGER.info(
        "Initializing %s integration with plaforms: %s with config: %s",
        DOMAIN,
        PLATFORMS,
        config,
    )

    # Mettre ici un eventuel code permettant l'initialisation de l'intégration
    # Ca peut être une connexion sur le Cloud qui fournit les données par ex
    # (pas nécessaire pour le tuto)

    # L'argument config contient votre fichier configuration.yaml
    # my_config = config_entry.get(DOMAIN)  # pylint: disable=unused-variable
    # username = my_config[CONF_USERNAME]
    # password = my_config[CONF_PASSWORD]
    # club = my_config["club"]

    # hass.data[DOMAIN] = {
    #     "username": username,
    #     "password": password,
    #     "club": club
    # }
    # Return boolean to indicate that initialization was successful.
    return True

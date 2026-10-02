"""Thermia number integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ThermiaDataUpdateCoordinator
from .numbers.cooling_temperature_number import ThermiaCoolingTemperatureNumber


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Thermia numbers."""

    coordinator: ThermiaDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    hass_thermia_numbers = []

    for idx, heat_pump in enumerate(coordinator.data.heat_pumps):
        # Thermia hides the cooling temperature register while cooling is off,
        # so also create the entity when only the cooling switch is there
        if (
            heat_pump.cooling_temperature is not None
            or heat_pump.cooling_switch_state is not None
        ):
            hass_thermia_numbers.append(
                ThermiaCoolingTemperatureNumber(coordinator, idx)
            )

    async_add_entities(hass_thermia_numbers)

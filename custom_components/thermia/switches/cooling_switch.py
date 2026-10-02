"""Thermia cooling switch integration."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN
from ..coordinator import ThermiaDataUpdateCoordinator


class ThermiaCoolingSwitch(
    CoordinatorEntity[ThermiaDataUpdateCoordinator], SwitchEntity
):
    """Representation of an Thermia cooling switch."""

    def __init__(self, coordinator, idx: int):
        super().__init__(coordinator)
        self.idx: int = idx

    @property
    def available(self):
        """Return True if entity is available."""
        heat_pump = self.coordinator.data.heat_pumps[self.idx]
        return (
            super().available
            and heat_pump.is_online
            and heat_pump.cooling_switch_state is not None
        )

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{self.coordinator.data.heat_pumps[self.idx].name} Cooling"

    @property
    def unique_id(self):
        """Return the unique ID of the switch."""
        return f"{self.coordinator.data.heat_pumps[self.idx].name}_cooling"

    @property
    def icon(self):
        """Return the icon of the switch."""
        return "mdi:snowflake"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.data.heat_pumps[self.idx].id)},
            "name": self.coordinator.data.heat_pumps[self.idx].name,
            "manufacturer": "Thermia",
            "model": self.coordinator.data.heat_pumps[self.idx].model,
            "model_id": self.coordinator.data.heat_pumps[self.idx].model_id,
        }

    @property
    def device_class(self):
        """Return the device class of the switch."""
        return "switch"

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self.coordinator.data.heat_pumps[self.idx].cooling_switch_state == 1

    async def async_turn_on(self, **kwargs):
        """Turn on the switch."""
        await self.hass.async_add_executor_job(
            lambda: self.coordinator.data.heat_pumps[self.idx].set_cooling_switch_state(
                1
            )
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn off the switch."""
        await self.hass.async_add_executor_job(
            lambda: self.coordinator.data.heat_pumps[self.idx].set_cooling_switch_state(
                0
            )
        )
        await self.coordinator.async_request_refresh()

    async def async_toggle(self, **kwargs):
        """Toggle the switch."""
        if self.is_on:
            await self.async_turn_off()
        else:
            await self.async_turn_on()

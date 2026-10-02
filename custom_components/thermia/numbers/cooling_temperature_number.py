"""Thermia cooling target temperature number integration."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN
from ..coordinator import ThermiaDataUpdateCoordinator


class ThermiaCoolingTemperatureNumber(
    CoordinatorEntity[ThermiaDataUpdateCoordinator], NumberEntity
):
    """Representation of an Thermia cooling target temperature."""

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
            and heat_pump.cooling_temperature is not None
            and heat_pump.cooling_min_temperature_value is not None
            and heat_pump.cooling_max_temperature_value is not None
        )

    @property
    def name(self):
        """Return the name of the number."""
        return f"{self.coordinator.data.heat_pumps[self.idx].name} Cooling Target Temperature"

    @property
    def unique_id(self):
        """Return the unique ID of the number."""
        return f"{self.coordinator.data.heat_pumps[self.idx].name}_cooling_target_temperature"

    @property
    def icon(self):
        """Return the icon of the number."""
        return "mdi:snowflake-thermometer"

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
        """Return the device class of the number."""
        return NumberDeviceClass.TEMPERATURE

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement of the number."""
        return UnitOfTemperature.CELSIUS

    @property
    def native_min_value(self):
        """Return the minimum value."""
        min_value = self.coordinator.data.heat_pumps[
            self.idx
        ].cooling_min_temperature_value
        return min_value if min_value is not None else super().native_min_value

    @property
    def native_max_value(self):
        """Return the maximum value."""
        max_value = self.coordinator.data.heat_pumps[
            self.idx
        ].cooling_max_temperature_value
        return max_value if max_value is not None else super().native_max_value

    @property
    def native_step(self):
        """Return the step value."""
        step = self.coordinator.data.heat_pumps[self.idx].cooling_temperature_step
        return step if step is not None else super().native_step

    @property
    def native_value(self):
        """Return the cooling target temperature."""
        return self.coordinator.data.heat_pumps[self.idx].cooling_temperature

    async def async_set_native_value(self, value: float):
        """Set new cooling target temperature."""
        # HA doesn't enforce the step, and unit conversion (e.g. from °F) gives
        # fractions, so round to the heat pump's step before writing
        step = self.native_step or 1
        temperature = round(round(value / step) * step, 2)
        if float(temperature).is_integer():
            temperature = int(temperature)
        await self.hass.async_add_executor_job(
            lambda: self.coordinator.data.heat_pumps[self.idx].set_cooling_temperature(
                temperature
            )
        )
        await self.coordinator.async_request_refresh()

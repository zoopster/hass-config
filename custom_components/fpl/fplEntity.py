"""Fpl Entity class"""

from datetime import datetime, timedelta

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,  # Imported if you need to set _attr_state_class
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

# Updated import for kWh unit:
from homeassistant.const import (
    CURRENCY_DOLLAR,
    UnitOfEnergy,
)

from .const import DOMAIN, VERSION, ATTRIBUTION


class FplEntity(CoordinatorEntity, SensorEntity):
    """FPL base entity"""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator, config_entry, account, sensorName):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.account = account
        self.sensorName = sensorName

    @property
    def unique_id(self):
        """Return the ID of this device."""
        sensorName = self.sensorName.lower().replace(" ", "")
        return f"{DOMAIN}{self.account}{sensorName}"

    @property
    def name(self):
        """Return a friendly name for this entity."""
        return f"{DOMAIN.upper()} {self.account} {self.sensorName}"

    @property
    def device_info(self):
        """Return device information for this entity."""
        return {
            "identifiers": {(DOMAIN, self.account)},
            "name": f"FPL {self.account}",
            "model": VERSION,
            "manufacturer": "Florida Power & Light",
            "configuration_url": "https://www.fpl.com/my-account/residential-dashboard.html",
        }

    def customAttributes(self) -> dict:
        """Override this method in child classes to add custom attributes."""
        return {}

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attributes = {"attribution": ATTRIBUTION}
        attributes.update(self.customAttributes())
        return attributes

    def getData(self, field):
        """Get data from the coordinator for this sensor."""
        if self.coordinator.data is not None:
            account_data = self.coordinator.data.get(self.account)
            if account_data is not None:
                return account_data.get(field, None)
        return None


class FplEnergyEntity(FplEntity):
    """Represents an energy sensor (in kWh)."""

    _attr_device_class = SensorDeviceClass.ENERGY
    # Switch from ENERGY_KILO_WATT_HOUR to UnitOfEnergy.KILO_WATT_HOUR
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_icon = "mdi:flash"

    @property
    def last_reset_not_use(self) -> datetime:
        """
        Example method if you ever need a daily reset time.
        Not typically used in the modern approach, but left here
        if you'd like to implement older style sensor resets.
        """
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        return datetime.combine(yesterday, datetime.min.time())


class FplMoneyEntity(FplEntity):
    """Represents a money sensor (in dollars)."""

    # If you prefer "USD" as the native unit, just replace CURRENCY_DOLLAR with "USD".
    _attr_native_unit_of_measurement = CURRENCY_DOLLAR
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_icon = "mdi:currency-usd"


class FplDateEntity(FplEntity):
    """Represents a date-based sensor."""

    _attr_icon = "mdi:calendar"


class FplDayEntity(FplEntity):
    """Represents a sensor measured in days."""

    _attr_native_unit_of_measurement = "days"
    _attr_icon = "mdi:calendar"

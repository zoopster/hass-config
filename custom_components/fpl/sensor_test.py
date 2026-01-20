"""Test Sensors"""

from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import STATE_UNKNOWN

from .fplEntity import FplEnergyEntity


class TestSensor(FplEnergyEntity):
    """Daily Usage KWh Sensor (Test)"""

    # If this sensor represents a continuously increasing value (like a meter),
    # TOTAL_INCREASING is appropriate.
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Test Sensor")

    @property
    def native_value(self):
        data = self.getData("daily_usage")

        if data and len(data) > 0 and "usage" in data[-1]:
            return data[-1]["usage"]

        return STATE_UNKNOWN

    @property
    def last_reset(self) -> datetime | None:
        # Only used/needed if you want older style billing resets or to help HA
        # understand when your meter was reset (for TOTAl_INCREASING).
        data = self.getData("daily_usage")
        if data and len(data) > 0 and "readTime" in data[-1]:
            date = data[-1]["readTime"]
            last_reset = datetime.combine(date, datetime.min.time())
            print(f"Setting last_reset to: {last_reset}")
            return last_reset
        return None

    def customAttributes(self):
        """Return any custom attributes for the sensor."""
        print("Setting custom attributes")
        data = self.getData("daily_usage")

        attributes = {}
        if data and len(data) > 0 and "readTime" in data[-1]:
            date = data[-1]["readTime"]
            attributes["date"] = date
            # Example of a possible last_reset in attributes (not typically needed if `last_reset` property is used)
            # attributes["last_reset"] = date - timedelta(days=1)

        return attributes

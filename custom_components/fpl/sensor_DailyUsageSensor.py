"""Daily Usage Sensors"""

from datetime import timedelta, datetime

# Updated imports:
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

from .fplEntity import FplEnergyEntity, FplMoneyEntity


class FplDailyUsageSensor(FplMoneyEntity):
    """Daily Usage Cost Sensor (monetary)"""

    # If this sensor represents the cost *just for today* (not cumulative),
    # then use MEASUREMENT. If it's a cumulative total cost so far, use TOTAL_INCREASING.
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Usage")

    @property
    def native_value(self):
        data = self.getData("DailyUsage")
        self._attr_native_value = data["billingCharge"]
        return self._attr_native_value

    @property
    def last_reset(self) -> datetime:
        data = self.getData("DailyUsage")
        # Given that the readTime happens at midnight, we can use the previous day's readTime as the last reset.
        # The assumption here is that it is always at midnight.
        # But we can always get the previous day's readTime if this assumption proves to be incorrect.
        return data["readTime"] - timedelta(days=1)

    def customAttributes(self):
        """Return the state attributes."""
        data = self.getData("DailyUsage")
        attributes = {
            "date": data["readTime"].strftime("%Y-%m-%d"),
        }

        return attributes


class FplDailyUsageKWHSensor(FplEnergyEntity):
    """Daily Usage KWH Sensor"""

    # For daily usage, you might choose TOTAL if it's the total for that day
    # or TOTAL_INCREASING if you're incrementing throughout the day.
    _attr_state_class = SensorStateClass.TOTAL
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Usage KWH")

    @property
    def native_value(self):
        data = self.getData("DailyUsage")
        self._attr_native_value = data["kwhActual"]
        return self._attr_native_value

    @property
    def last_reset(self) -> datetime:
        """An optional last_reset property for daily totals."""
        data = self.getData("DailyUsage")
        # Given that the readTime happens at midnight, we can use the previous day's readTime as the last reset.
        # The assumption here is that it is always at midnight.
        # But we can always get the previous day's readTime if this assumption proves to be incorrect.
        return data["readTime"] - timedelta(days=1)

    def customAttributes(self):
        """Return any additional attributes."""
        data = self.getData("DailyUsage")
        return {
            "date": data["readTime"].strftime("%Y-%m-%d"),
        }


class FplDailyReceivedKWHSensor(FplEnergyEntity):
    """Daily Received KWH Sensor"""

    _attr_state_class = SensorStateClass.TOTAL
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Received KWH")

    @property
    def native_value(self):
        data = self.getData("DailyUsage")
        self._attr_native_value = data["kwhActual"]
        return self._attr_native_value

    @property
    def last_reset(self) -> datetime | None:
        data = self.getData("DailyUsage")
        return data["readTime"] - timedelta(days=1)
        return None

    def customAttributes(self):
        """Return any additional attributes."""
        data = self.getData("DailyUsage")
        attributes = {
            "date": data["readTime"].strftime("%Y-%m-%d"),
        }
        return attributes


class FplDailyDeliveredKWHSensor(FplEnergyEntity):
    """Daily Delivered KWH Sensor"""

    _attr_state_class = SensorStateClass.TOTAL
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Delivered KWH")

    @property
    def native_value(self):
        data = self.getData("DailyUsage")
        self._attr_native_value = data["netDeliveredKwh"]
        return self._attr_native_value

    @property
    def last_reset(self) -> datetime | None:
        data = self.getData("DailyUsage")
        return data["readTime"] - timedelta(days=1)

    def customAttributes(self):
        """Return any additional attributes."""
        data = self.getData("DailyUsage")
        attributes = {
            "date": data["readTime"].strftime("%Y-%m-%d"),
        }
        return attributes


class FplDailyReceivedReading(FplEnergyEntity):
    """Daily Received Reading (Meter)"""

    # If this reading is continuously increasing, TOTAL_INCREASING is correct:
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Received Reading")

    @property
    def native_value(self):
        data = self.getData("DailyUsage")
        self._attr_native_value = data["reading"]
        return self._attr_native_value


class FplDailyDeliveredReading(FplEnergyEntity):
    """Daily Delivered Reading (Meter)"""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Delivered reading")

    @property
    def native_value(self):
        data = self.getData("DailyUsage")
        self._attr_native_value = data["netDeliveredReading"]
        return self._attr_native_value

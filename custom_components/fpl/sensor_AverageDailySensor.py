"""Average daily sensors"""

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from .fplEntity import FplMoneyEntity


class DailyAverageSensor(FplMoneyEntity):
    """Average daily sensor, use budget value if available, otherwise use actual daily values"""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Average")

    @property
    def native_value(self):
        daily_avg = self.getData("dailyAvg")
        if daily_avg is not None:
            self._attr_native_value = daily_avg
        return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        # Add any extra attributes you want to expose here
        attributes = {}
        return attributes


class BudgetDailyAverageSensor(FplMoneyEntity):
    """Budget daily average sensor"""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Budget Daily Average")

    @property
    def native_value(self):
        budget_billing_daily_avg = self.getData("budget_billing_daily_avg")
        if budget_billing_daily_avg is not None:
            self._attr_native_value = budget_billing_daily_avg
        return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        return attributes


class ActualDailyAverageSensor(FplMoneyEntity):
    """Actual daily average sensor"""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Actual Daily Average")

    @property
    def native_value(self):
        daily_avg = self.getData("dailyAvg")
        if daily_avg is not None:
            self._attr_native_value = daily_avg
        return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        return attributes

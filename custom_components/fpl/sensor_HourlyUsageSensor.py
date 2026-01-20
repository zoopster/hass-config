"""Hourly Usage Sensors"""

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass


from .fplEntity import FplEnergyEntity, FplMoneyEntity
from .const import DOMAIN


class FplHourlyUsageSensor(FplMoneyEntity):
    """Hourly Usage Cost Sensor (monetary)"""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Hourly Cost")

    @property
    def statistic_id(self):
        return f"{DOMAIN}:{self.account}:hourly_cost"

    @property
    def native_value(self):
        data = self.getData("HourlyUsage")
        if data:
            self._attr_native_value = data[-1]["billingCharged"]
        return self._attr_native_value

    def customAttributes(self):
        """Return any additional attributes."""
        data = self.getData("HourlyUsage")
        return (
            {
                "date": data[-1]["readTime"],
                "hour": data[-1]["hour"],
            }
            if data
            else {}
        )


class FplHourlyUsageKWHSensor(FplEnergyEntity):
    """
    Hourly Usage KWh Sensor
    This sensor will always return the previous day's last hour's usage.
    This is because the FPL API only returns the previous day's usage.
    This sensor is only useful for Debugging or Automations.
    The actual usage is uploaded as an external statistic in the coordinator.
    """

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Hourly Usage KWH")

    @property
    def statistic_id(self):
        return f"{DOMAIN}:{self.account}:hourly_usage"

    @property
    def native_value(self):
        data = self.getData("HourlyUsage")
        if data:
            self._attr_native_value = data[-1]["kwhActual"]
        return self._attr_native_value

    def customAttributes(self):
        """Return any additional attributes."""
        data = self.getData("HourlyUsage")
        return (
            {
                "date": data[-1]["readTime"],
                "hour": data[-1]["hour"],
            }
            if data
            else {}
        )


# class FplHourlyReceivedKWHSensor(FplEnergyEntity):
#     """Hourly Received KWh Sensor"""

#     # If you’re tracking an hourly usage that resets each hour, use MEASUREMENT or TOTAL.
#     # If it's a continuously growing total, use TOTAL_INCREASING.
#     _attr_device_class = SensorDeviceClass.ENERGY
#     _attr_state_class = SensorStateClass.MEASUREMENT

#     def __init__(self, coordinator, config, account):
#         super().__init__(coordinator, config, account, "Hourly Received KWH")

#     @property
#     def statistic_id(self) -> str:
#         return self.entity_id

#     # Uncomment if you want to provide a reading:
#     #
#     # @property
#     # def native_value(self):
#     #     data = self.getData("hourly_usage")
#     #     if data and len(data) > 0 and "netReceived" in data[-1]:
#     #         self._attr_native_value = data[-1]["netReceived"]
#     #     return self._attr_native_value
#     #
#     # @property
#     # def last_reset(self) -> datetime | None:
#     #     data = self.getData("hourly_usage")
#     #     if data and len(data) > 0 and "readTime" in data[-1]:
#     #         return data[-1]["readTime"]
#     #     return None

#     def customAttributes(self):
#         return {}


# class FplHourlyDeliveredKWHSensor(FplEnergyEntity):
#     """Hourly Delivered KWh Sensor"""

#     _attr_device_class = SensorDeviceClass.ENERGY
#     _attr_state_class = SensorStateClass.MEASUREMENT

#     def __init__(self, coordinator, config, account):
#         super().__init__(coordinator, config, account, "Hourly Delivered KWH")

#     # @property
#     # def native_value(self):
#     #     data = self.getData("hourly_usage")
#     #     if data and len(data) > 0 and "netDelivered" in data[-1]:
#     #         self._attr_native_value = data[-1]["netDelivered"]
#     #     return self._attr_native_value
#     #
#     # @property
#     # def last_reset(self) -> datetime | None:
#     #     data = self.getData("hourly_usage")
#     #     if data and len(data) > 0 and "readTime" in data[-1]:
#     #         return data[-1]["readTime"]
#     #     return None

#     def customAttributes(self):
#         return {}


# class FplHourlyReadingKWHSensor(FplEnergyEntity):
#     """Hourly Reading KWh Sensor (Meter)"""

#     # If this reading is a continuously increasing meter, use TOTAL_INCREASING.
#     _attr_device_class = SensorDeviceClass.ENERGY
#     _attr_state_class = SensorStateClass.TOTAL_INCREASING

#     def __init__(self, coordinator, config, account):
#         super().__init__(coordinator, config, account, "Hourly Reading KWH")

#     # @property
#     # def native_value(self):
#     #     data = self.getData("hourly_usage")
#     #     if data and len(data) > 0 and "reading" in data[-1]:
#     #         self._attr_native_value = data[-1]["reading"]
#     #     return self._attr_native_value

#     def customAttributes(self):
#         return {}

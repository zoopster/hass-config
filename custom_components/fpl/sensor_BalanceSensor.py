"""Balance sensors"""

from .fplEntity import FplMoneyEntity
from .fplEntity import FplDateEntity


class BalanceSensor(FplMoneyEntity):
    """balance sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Balance Due")

    @property
    def native_value(self):
        self._attr_native_value = self.getData("balance")
        return self._attr_native_value


class BalanceDueDateSensor(FplDateEntity):
    """balance due date sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Balance Due Date")

    @property
    def native_value(self):
        self._attr_native_value = self.getData("balance_due_date")
        return self._attr_native_value

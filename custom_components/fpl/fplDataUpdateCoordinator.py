"""Data Update Coordinator"""

import asyncio
import logging
from datetime import timedelta
from zoneinfo import ZoneInfo

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics,
    StatisticData,
    StatisticMetaData,
    get_last_statistics,
)
from homeassistant.core import HomeAssistant
from homeassistant.components import recorder

from homeassistant.util import dt as dt_util

from .fplapi import FplApi
from .const import DOMAIN, CONF_ACCOUNTS

# FPL operates in Florida, which is in the Eastern timezone
FPL_TIMEZONE = ZoneInfo("America/New_York")

SCAN_INTERVAL = timedelta(seconds=1200)
# Anything more than 15 days may cause Cloudflare to block all of our requests.
HOURLY_USAGE_BACKFILL_DAYS = 15

_LOGGER: logging.Logger = logging.getLogger(__package__)


class FplDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: FplApi) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _get_last_sum(self, stat_id: str):
        def _read():
            return get_last_statistics(
                hass=self.hass,
                number_of_stats=1,
                statistic_id=stat_id,
                convert_units=False,
                types={"sum"},
            )

        result = await recorder.get_instance(self.hass).async_add_executor_job(_read)

        if rows := result.get(stat_id):
            return float(rows[0]["sum"] or 0.0), dt_util.utc_from_timestamp(
                rows[0]["start"]
            )
        return 0.0, None

    async def _publish_hourly_statistics(self, account: str, hourly: list) -> None:
        stat_id_usage = f"{DOMAIN}:{account}_hourly_usage"
        stat_id_cost = f"{DOMAIN}:{account}_hourly_cost"

        usage_sum, last_usage_start = await self._get_last_sum(stat_id_usage)
        cost_sum, last_cost_start = await self._get_last_sum(stat_id_cost)

        cost_stats = []
        usage_stats = []
        for h in sorted(hourly, key=lambda x: x.get("readTime")):
            cost = h.get("billingCharged")
            usage = h.get("kwhActual")

            read_time = h.get("readTime")
            if read_time is None:
                continue

            # Ensure read_time is timezone-aware in FPL's timezone (Eastern)
            if read_time.tzinfo is None:
                read_time = read_time.replace(tzinfo=FPL_TIMEZONE)

            # Convert to UTC for Home Assistant statistics
            read_time_utc = read_time.astimezone(dt_util.UTC)
            read_time_utc = read_time_utc.replace(minute=0, second=0, microsecond=0)
            start = read_time_utc - timedelta(hours=1)

            if cost is not None:
                if not last_cost_start or start > last_cost_start:
                    cost_sum += cost
                    cost_stat = StatisticData(
                        start=start,
                        sum=cost_sum,
                        state=cost,
                    )
                    cost_stats.append(cost_stat)

            if usage is not None:
                if not last_usage_start or start > last_usage_start:
                    usage_sum += usage
                    usage_stat = StatisticData(
                        start=start,
                        sum=usage_sum,
                        state=usage,
                    )
                    usage_stats.append(usage_stat)

        if cost_stats:
            metadata = StatisticMetaData(
                has_mean=False,
                has_sum=True,
                source=DOMAIN,
                name=f"FPL {account} Hourly Cost",
                statistic_id=stat_id_cost,
                unit_of_measurement="USD",
            )

            async_add_external_statistics(self.hass, metadata, cost_stats)

        if usage_stats:
            metadata = StatisticMetaData(
                has_mean=False,
                has_sum=True,
                source=DOMAIN,
                name=f"FPL {account} Hourly Usage",
                statistic_id=stat_id_usage,
                unit_of_measurement="kWh",
            )

            async_add_external_statistics(self.hass, metadata, usage_stats)

        return cost_sum, usage_sum

    async def _async_update_data(self):
        try:
            data = await self.api.async_get_data()

            # Backfill hourly cost for accounts
            for account in data.get(CONF_ACCOUNTS, []):
                premise = data.get(account, {}).get("premise")
                # If there is already hourly usage statistics, then only backfill the yesterday.
                _, last_sum_start = await self._get_last_sum(
                    f"{DOMAIN}:{account}_hourly_usage"
                )
                if last_sum_start is not None:
                    date = dt_util.now() - timedelta(days=1)
                    hourly = await self.api.apiClient.get_hourly_usage(
                        account, premise, date
                    )
                    await self._publish_hourly_statistics(account, hourly)
                else:
                    # Only backfill the full amount of days if the account has no hourly usage statistics.
                    # We need to start backwards. For example today - 360 days.
                    date = dt_util.now() - timedelta(days=HOURLY_USAGE_BACKFILL_DAYS)

                    all_hourly: list = []
                    for _ in range(HOURLY_USAGE_BACKFILL_DAYS):
                        hourly = await self.api.apiClient.get_hourly_usage(
                            account, premise, date
                        )
                        all_hourly.extend(hourly)
                        date = date + timedelta(days=1)
                        await asyncio.sleep(1)
                    if all_hourly:
                        await self._publish_hourly_statistics(account, all_hourly)

            return data
        except Exception as exception:
            raise UpdateFailed() from exception

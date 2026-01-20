import logging

from homeassistant.helpers.entity import Entity


class nooa:

    URL = "https://services.swpc.noaa.gov/products/noaa-scales.json"

    @staticmethod
    async def fetch(session, url):
        import json
        async with session.get(url) as response:
            return json.loads(await response.text())

    @staticmethod
    async def get_data():
        import aiohttp
        async with aiohttp.ClientSession() as session:
            html = await nooa.fetch(session, nooa.URL)
            return html


_LOGGER = logging.getLogger(__name__)

STATIC_DATA = {
    "S": ("Solar Radiation Storms",),
    "R": ("Radio Blackouts",),
    "G": ("Geomagnetic Storms",),
}


async def async_setup_platform(
        hass, config, async_add_entities, discovery_info=None):
    """Set up the sensors."""
    data = await nooa.get_data()
    entities = [
        NooaSensor(data, "R"),
        NooaSensor(data, "S"),
        NooaSensor(data, "G"),
    ]
    async_add_entities(entities)


class NooaSensor(Entity):
    """Representation of sensor."""

    def __init__(self, data, sensor_type):
        """Init the sensor."""
        self._unit = sensor_type
        self._attributes = {}
        self._state = data["0"][sensor_type]["Scale"]
        self.filter_attributes(data)
        self._name = STATIC_DATA[sensor_type][0]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def state(self):
        """Property for the state attributes."""
        return self._state

    @property
    def name(self):
        """Name property for sensor."""
        return self._name

    @property
    def state_attributes(self):
        """Property for the state attributes."""
        return self._attributes

    def filter_attributes(self, data):
        """Filter out data for this Sensor."""
        self._attributes = {
            "Yesterday": data["-1"][self._unit]["Scale"],
            "Tomorrow": data["1"][self._unit]["Scale"],
            "Day after tomorrow": data["2"][self._unit]["Scale"],
            "In three days": data["3"][self._unit]["Scale"]
        }

    async def async_update(self):
        """Fetch new state data for the sensor."""
        data = await nooa.get_data()
        self._state = data["0"][self._unit]["Scale"]
        self.filter_attributes(data)


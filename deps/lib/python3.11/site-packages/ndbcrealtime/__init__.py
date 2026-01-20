"""Simple PyPi Wrapper for the NOAA NDBC observation data."""

import logging
import json
import aiohttp
import xmltodict
import collections
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from datetime import datetime, timezone
import calendar
import asyncio

_LOGGER = logging.getLogger("surfline")

STATION_URL = "https://www.ndbc.noaa.gov/activestations.xml"
OBSERVATION_BASE_URL = "https://www.ndbc.noaa.gov/data/realtime2/"

class NDBC:
    def __init__(
        self, 
        station_id:str,
        session:aiohttp.ClientSession=None,
    ):
        self._station_id = station_id

        if not session:
            self._session = aiohttp.ClientSession()
        else:
            self._session = session

    async def close(self):
        await self._session.close()

    async def get_data(self):
        """Get the observation data and structure to meet defined spec."""
        stations = Stations()
        stations_list = await stations.list()
        await stations.close()
        
        if not stations_list[self._station_id]:
            raise ValueError(f"Station ID {self._station_id} is invalid.")

        station = stations_list[self._station_id]
        data = await self.get_json()
        
        structured = {}
        observation = {}

        """Structure the location details."""
        structured["location"] = {
            "latitude": float(station["@lat"]),
            "longitude": float(station["@lon"]),
            "elevation": int(station.get("@elev",0)),
            "name": station["@name"]
        }

        """Structure the observation time."""
        observation_time = datetime(
            int(data[1]["YY"]),
            int(data[1]["MM"]),
            int(data[1]["DD"]),
            int(data[1]["hh"]),
            int(data[1]["mm"]),
            tzinfo=timezone.utc
        )

        observation["time"] = {
            "utc_time": observation_time.isoformat(),
            "unix_time": calendar.timegm(observation_time.utctimetuple())
        }

        """Structure the observation wind."""
        observation["wind"] = {
            "direction": None,
            "direction_unit": data[0]["WDIR"],
            "direction_compass": None,
            "speed": None,
            "speed_unit": data[0]["WSPD"],
            "gusts": None,
            "gusts_unit": data[0]["GST"]
        }

        if data[1]["WDIR"] != "MM":
            observation["wind"]["direction"] = int(data[1]["WDIR"])
            observation["wind"]["direction_compass"] = self.compass_direction(float(data[1]["WDIR"]))

        if data[1]["WSPD"] != "MM":
            observation["wind"]["speed"] = float(data[1]["WSPD"])

        if data[1]["GST"] != "MM":
            observation["wind"]["gusts"] = float(data[1]["GST"])

        """Structure the observation waves."""
        observation["waves"] = {
            "height": None,
            "height_unit": data[0]["WVHT"],
            "period": None,
            "period_unit": data[0]["DPD"],
            "average_period": None,
            "average_period_unit": data[0]["APD"],
            "direction": None,
            "direction_unit": data[0]["MWD"],
            "direction_compass": None,
        }

        if data[1]["WVHT"] != "MM":
            observation["waves"]["height"] = float(data[1]["WVHT"])

        if data[1]["DPD"] != "MM":
            observation["waves"]["period"] = int(data[1]["DPD"])
        
        if data[1]["APD"] != "MM":
            observation["waves"]["average_period"] = int(data[1]["APD"])
        
        if data[1]["MWD"] != "MM":
            observation["waves"]["direction"] = int(data[1]["MWD"])
            observation["waves"]["direction_compass"] = self.compass_direction(float(data[1]["MWD"]))

        """Structure the observation weather."""
        observation["weather"] = {
            "pressure": None,
            "pressure_unit": data[0]["PRES"],
            "air_temperature": None,
            "air_temperature_unit": data[0]["ATMP"],
            "water_temperature": None,
            "water_temperature_unit": data[0]["WTMP"],
            "dewpoint": None,
            "dewpoint_unit": data[0]["DEWP"],
            "visibility": None,
            "visibility_unit": data[0]["VIS"],
            "pressure_tendency": None,
            "pressure_tendency_unit": data[0]["PTDY"],
            "tide": None,
            "tide_unit": data[0]["TIDE"]
        }

        if data[1]["PRES"] != "MM":
            observation["weather"]["pressure"] = float(data[1]["PRES"])

        if data[1]["ATMP"] != "MM":
            observation["weather"]["air_temperature"] = float(data[1]["ATMP"])

        if data[1]["WTMP"] != "MM":
            observation["weather"]["water_temperature"] = float(data[1]["WTMP"])

        if data[1]["DEWP"] != "MM":
            observation["weather"]["dewpoint"] = float(data[1]["DEWP"])

        if data[1]["VIS"] != "MM":
            observation["weather"]["visibility"] = float(data[1]["VIS"])

        if data[1]["PTDY"] != "MM":
            observation["weather"]["pressure_tendency"] = float(data[1]["PTDY"])

        if data[1]["TIDE"] != "MM":
            observation["weather"]["tide"] = float(data[1]["TIDE"])

        """Add the observation to the structured data and return."""
        structured["observation"] = observation

        return structured

    async def get_json(self):
        """Get the observation data from NOAA and convert to json object."""
        response = {}
        request_url = f"{OBSERVATION_BASE_URL}{self._station_id.upper()}.txt"
        col_specification = {
            "YY": (0,4),
            "MM": (5,7),
            "DD": (8,10),
            "hh": (11,13),
            "mm": (14,16),
            "WDIR": (17,21),
            "WSPD": (22,26),
            "GST": (27,31),
            "WVHT": (32,38),
            "DPD": (39,44),
            "APD": (45,48),
            "MWD": (49,52),
            "PRES": (53,60),
            "ATMP": (61,66),
            "WTMP": (67,72),
            "DEWP": (73,78),
            "VIS": (79,82),
            "PTDY": (83,88),
            "TIDE": (89,93)
        }

        async with await self._session.get(request_url) as resp:
            response = await resp.text()
        
        if response is not None and resp.status != 404:
            try:
                data = response.split("\n")
                data_json = []
                
                for line in data:
                    if line[0:3] == "#YY":
                        continue
                    thisline = {}
                    for key, colspec in col_specification.items():
                        thisline[key] = line[colspec[0]:colspec[1]].strip()
                    
                    data_json.append(thisline)

                return data_json
            except json.decoder.JSONDecodeError as error:
                raise ValueError(f"Error decoding data from NDBC ({error}).")
            except Exception as error:
                raise ValueError(f"Unknown error in NDBC data ({error})")
        elif resp.status == 404:
            raise ValueError(f"Invalid station ID ({self._station_id})")
        else:
            raise ConnectionError("Error getting data from NDBC.")
        

    def compass_direction(self, degrees:float):
        if degrees > 11.25 and degrees <= 33.75:
            return "NNE"
        elif degrees > 33.75 and degrees <= 56.25:
            return "NE"
        elif degrees > 56.25 and degrees <= 78.75:
            return "ENE"
        elif degrees > 78.75 and degrees <= 101.25:
            return "E"
        elif degrees > 101.25 and degrees <= 123.75:
            return "ESE"
        elif degrees > 123.75 and degrees <= 146.25:
            return "SE"
        elif degrees > 146.25 and degrees <= 168.75:
            return "SSE"
        elif degrees > 168.75 and degrees <= 191.25:
            return "S"
        elif degrees > 191.25 and degrees <= 213.75:
            return "SSW"
        elif degrees > 213.75 and degrees <= 236.25:
            return "SW"
        elif degrees > 236.25 and degrees <= 258.75:
            return "WSW"
        elif degrees > 258.75 and degrees <= 281.25:
            return "W"
        elif degrees > 281.25 and degrees <= 303.75:
            return "WNW"
        elif degrees > 303.75 and degrees <= 326.25:
            return "NW"
        elif degrees > 326.25 and degrees <= 348.75:
            return "NNW"

        return "N"


class Stations:
    def __init__(self) -> None:
        self._session = aiohttp.ClientSession()

    async def close(self):
        await self._session.close()
        
    async def list(self):
        response = ""

        async with await self._session.get(STATION_URL) as resp:
            response = await resp.text()

        try:
            my_dict = xmltodict.parse(response)
            json_data = json.dumps(my_dict)
        except:
            raise Exception("Error converting Hayward data to JSON.")

        stations = json.loads(json_data)
        list = {}

        for station in stations["stations"]["station"]:
            list[station["@id"]] = station

        return list

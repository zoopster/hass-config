"""Web client."""
import asyncio
import socket
import aiohttp
import async_timeout

import backoff

from integrationhelper.const import GOOD_HTTP_CODES


class WebClient:
    """Web client."""

    def __init__(self, session=None, logger=None):
        """
        Initialize.

        Sample Usage:
        from integrationhelper.webclient import WebClient
        url = "https://sample.com/api"
        webclient = WebClient()
        print(await webclient.async_get_json(url))
        """
        self.session = session
        if logger is not None:
            self.logger = logger
        else:
            from integrationhelper import Logger

            self.logger = Logger(__name__)

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def async_get_json(self, url: str, custom_headers: dict = None):
        """Get json response from server."""
        try:
            assert isinstance(url, str)
        except AssertionError:
            self.logger.error(f"({url}) is not a string.")
            return None

        try:
            assert custom_headers is None or isinstance(custom_headers, dict)
        except AssertionError:
            self.logger.error(f"({custom_headers}) is not a dict.")
            return None


        headers = {"Content-Type": "application/json"}
        if custom_headers is not None:
            for header in custom_headers:
                headers[header] = custom_headers[header]

        jsondata = None
        try:
            if self.session is not None:
                async with async_timeout.timeout(10, loop=asyncio.get_event_loop()):
                    response = await self.session.get(url, headers=headers)
                    if response.status not in GOOD_HTTP_CODES:
                        self.logger.error(
                            f"Recieved HTTP code ({response.status}) from {url}"
                        )
                        return jsondata
                    jsondata = await response.json()
            else:
                async with aiohttp.ClientSession() as session:
                    async with async_timeout.timeout(10, loop=asyncio.get_event_loop()):
                        response = await session.get(url, headers=headers)
                        if response.status not in GOOD_HTTP_CODES:
                            self.logger.error(
                                f"Recieved HTTP code ({response.status}) from {url}"
                            )
                            return jsondata
                        jsondata = await response.json()

            self.logger.debug(jsondata)

        except asyncio.TimeoutError as error:
            self.logger.error(
                f"Timeout error fetching information from {url} - ({error})"
            )
        except (KeyError, TypeError) as error:
            self.logger.error(f"Error parsing information from {url} - ({error})")
        except (aiohttp.ClientError, socket.gaierror) as error:
            self.logger.error(f"Error fetching information from {url} - ({error})")
        except Exception as error:  # pylint: disable=broad-except
            self.logger.error(f"Something really wrong happend! - ({error})")
        return jsondata

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def async_get_text(self, url: str, custom_headers: dict = None):
        """Get text response from server."""
        try:
            assert isinstance(url, str)
        except AssertionError:
            self.logger.error(f"({url}) is not a string.")
            return None

        try:
            assert url is None or isinstance(custom_headers, dict)
        except AssertionError:
            self.logger.error(f"({custom_headers}) is not a dict.")
            return None

        headers = {"Content-Type": "application/json"}
        if custom_headers is not None:
            for header in custom_headers:
                headers[header] = custom_headers[header]

        textdata = None
        try:
            if self.session is not None:
                async with async_timeout.timeout(10, loop=asyncio.get_event_loop()):
                    response = await self.session.get(url, headers=headers)
                    if response.status not in GOOD_HTTP_CODES:
                        self.logger.error(
                            f"Recieved HTTP code ({response.status}) from {url}"
                        )
                        return textdata
                    textdata = await response.text()
            else:
                async with aiohttp.ClientSession() as session:
                    async with async_timeout.timeout(10, loop=asyncio.get_event_loop()):
                        response = await session.get(url, headers=headers)
                        if response.status not in GOOD_HTTP_CODES:
                            self.logger.error(
                                f"Recieved HTTP code ({response.status}) from {url}"
                            )
                            return textdata
                        textdata = await response.text()

            self.logger.debug(textdata)

        except asyncio.TimeoutError as error:
            self.logger.error(
                f"Timeout error fetching information from {url} - ({error})"
            )
        except (KeyError, TypeError) as error:
            self.logger.error(f"Error parsing information from {url} - ({error})")
        except (aiohttp.ClientError, socket.gaierror) as error:
            self.logger.error(f"Error fetching information from {url} - ({error})")
        except Exception as error:  # pylint: disable=broad-except
            self.logger.error(f"Something really wrong happend! - ({error})")
        return textdata

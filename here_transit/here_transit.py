"""A module to query the HERE Transit API v8."""
from __future__ import annotations

import asyncio
import json
import socket
from datetime import datetime
from importlib import metadata
from typing import Any, Dict, List, MutableMapping

import aiohttp
import async_timeout
from yarl import URL

from .exceptions import (
    HERETransitConnectionError,
    HERETransitDepartureArrivalTooCloseError,
    HERETransitError,
    HERETransitNoRouteFoundError,
    HERETransitNoTransitRouteFoundError,
    HERETransitTooManyRequestsError,
    HERETransitUnauthorizedError,
)
from .model import Place, Return, TransitMode, UnitSystem

SCHEME = "https"
API_HOST = "transit.router.hereapi.com"
API_VERSION = "/v8"
ROUTES_PATH = "routes"


class HERETransitApi:
    """Main class for handling connections with the HERE Transit API v8."""

    def __init__(
        self,
        api_key: str,
        request_timeout: int = 10,
        session: aiohttp.client.ClientSession | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Initialize connection with HERE Transit.
        Class constructor for setting up an HERETransitApi object to
        communicate with the HERE Transit API.
        Args:
            api_key: A key generated specifically to authenticate API requests.
            request_timeout: Max timeout to wait for a response from the API.
            session: Optional, shared, aiohttp client session.
            user_agent: Defaults to here_transit/<version>.
        """
        self._session = session
        self._api_key = api_key
        self._close_session = False

        self.request_timeout = request_timeout
        self.user_agent = user_agent

        if user_agent is None:
            version = metadata.version(__package__)
            self.user_agent = f"here_transit/{version}"

    async def request(
        self,
        uri: str,
        params: MutableMapping[str, str | List[str]],
        method: str = "GET",
    ) -> Any:
        """Handle a request to the HERE Transit API.
        Make a request against the HERE Transit API and handles the response.
        Args:
            uri: The request URI on the HERE Transit API to call.
            method: HTTP method to use for the request; e.g., GET, POST.
            data: RAW HTTP request data to send with the request.
            json_data: Dictionary of data to send as JSON with the request.
            params: Mapping of request parameters to send with the request.
        Returns:
            The response from the API. In case the response is a JSON response,
            the method will return a decoded JSON response as a Python
            dictionary. In other cases, it will return the RAW text response.
        Raises:
            HERETransitConnectionError: An error occurred while communicating
                with the HERE Transit API (connection issues).
            HERETransitError: An error occurred while processing the
                response from the HERE Transit API (invalid data).
        """
        url = URL.build(scheme=SCHEME, host=API_HOST, path=API_VERSION) / uri

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
            "DNT": "1",
        }
        params["apiKey"] = self._api_key

        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True

        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self._session.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                )
        except asyncio.TimeoutError as exception:
            raise HERETransitConnectionError(
                "Timeout occurred while connecting to the HERE Transit API."
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise HERETransitConnectionError(
                "Error occurred while communicating with the HERE Transit API."
            ) from exception

        content_type = response.headers.get("Content-Type", "")
        contents = await response.read()
        decoded_contents = contents.decode("utf8")
        if "application/json" not in content_type:
            raise HERETransitError(response.status, {"message": decoded_contents})
        if response.status // 100 in [4, 5]:
            response.close()

            if response.status == 401:
                raise HERETransitUnauthorizedError(
                    json.loads(decoded_contents)["error_description"]
                )
            if response.status == 429:
                raise HERETransitTooManyRequestsError(
                    json.loads(decoded_contents)["error_description"]
                )

            raise HERETransitError(response.status, json.loads(decoded_contents))

        return await response.json()

    async def route(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        origin: Place,
        destination: Place,
        pedestrian_peed: int = 1,
        pedestrian_max_distance: int = 2000,
        alternatives: int = 0,
        units: UnitSystem = UnitSystem.METRIC,
        lang: str = "en-US",
        changes: int | None = None,
        included_modes: List[TransitMode] | None = None,
        excluded_modes: List[TransitMode] | None = None,
        return_values: List[Return] | None = None,
        departure_time: datetime | None = None,
        arrival_time: datetime | None = None,
    ) -> Any:
        """Get the route.
        Args:
            origin: Latitude and longitude of the origin.
            destination: Latitude and longitude of the destination.
            pedestrianSpeed: Walking speed in meters per second.
            pedestrianMaxDistance: Maximum allowed walking distance in meters.
            alternatives: Number of alternative routes to return.
            units: Unitsystem to use.
            lang: IETF BCP 47 compatible language identifier.
            changes: Maximum number of changes/transfers. None means unlimited.
            included_modes: Included TransitModes. None means all.
            excluded_modes: Excluded TransitModes. None means none.
            return_values: HERE Transit API return values to request.
            departure_time: Departure time.
            arrival_time: Arrival time.
        Returns:
            The response from the API.
        Raises:
            HERETransitConnectionError: An error occurred while communicating
                with the HERE Transit API (connection issues).
            HERETransitError: An error occurred while processing the
                response from the HERE Transit API (invalid data).
        """
        if included_modes is not None and excluded_modes is not None:
            if len(included_modes) > 0 and len(excluded_modes) > 0:
                raise ValueError("Cannot include and exclude at the same time")

        params: MutableMapping[str, str | List[str]] = {  # type: ignore
            "origin": f"{origin.latitude},{origin.longitude}",
            "destination": f"{destination.latitude},{destination.longitude}",
            "pedestrianSpeed": str(pedestrian_peed),
            "pedestrianMaxDistance": str(pedestrian_max_distance),
            "alternatives": str(alternatives),
            "units": units.value,
            "lang": lang,
        }
        if changes is not None:
            params["changes"] = str(changes)
        if included_modes is not None:
            params["modes"] = ",".join(m.value for m in included_modes)
        if excluded_modes is not None:
            params["modes"] = ",".join(f"-{m.value}" for m in excluded_modes)
        if return_values is not None:
            params["return"] = ",".join(r.value for r in return_values)
        if departure_time is not None:
            params["departureTime"] = departure_time.isoformat(timespec="seconds")
        if arrival_time is not None:
            params["arrivalTime"] = arrival_time.isoformat(timespec="seconds")

        response = await self.request(uri=ROUTES_PATH, params=params)

        if len(response["routes"]) < 1:
            raise_error_from_notices(response["notices"])
        return response

    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> HERETransitApi:
        """Async enter.
        Returns:
            The HERETransitApi object.
        """
        return self

    async def __aexit__(self, *_exc_info) -> None:
        """Async exit.
        Args:
            _exc_info: Exec type.
        """
        await self.close()


def raise_error_from_notices(notices: List[Dict[str, str]]) -> None:
    """Raise the correct error for the contained notices."""
    errors = {notice["code"]: notice["title"] for notice in notices}

    if (title := errors.get("departureArrivalTooClose")) is not None:
        raise HERETransitDepartureArrivalTooCloseError(title)
    if (title := errors.get("noTransitRouteFound")) is not None:
        raise HERETransitNoTransitRouteFoundError(title)
    if (title := errors.get("noRouteFound")) is not None:
        raise HERETransitNoRouteFoundError(title)

    raise HERETransitError(",".join(errors.values()))

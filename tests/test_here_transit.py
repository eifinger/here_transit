"""Tests for `here_transit.here_transit`."""
import os
from datetime import datetime

import aiohttp
import pytest

from here_transit.exceptions import HERETransitError, HERETransitUnauthorizedError
from here_transit.here_transit import API_HOST, API_VERSION, ROUTES_PATH, HERETransitApi
from here_transit.model import Place, Return, TransitMode


@pytest.mark.asyncio
async def test_car_route(aresponses):
    """Test getting a route."""
    aresponses.add(
        API_HOST,
        f"{API_VERSION}/{ROUTES_PATH}",
        "GET",
        aresponses.Response(
            text=load_json_fixture("transit_route_response.json"),
            status=200,
            content_type="application/json",
        ),
    )
    async with aiohttp.ClientSession() as session:
        here_api = HERETransitApi(api_key="key", session=session)
        response = await here_api.route(
            included_modes=[TransitMode.BUS],
            origin=Place(latitude=50.12778680095556, longitude=8.582081794738771),
            destination=Place(latitude=50.060940891421765, longitude=8.336477279663088),
            return_values=[Return.TRAVEL_SUMMARY, Return.POLYLINE],
            departure_time=datetime.now(),
        )

        assert response["routes"][0]["sections"][0]["travelSummary"]["duration"] == 1140


@pytest.mark.asyncio
async def test_invalid_key(aresponses):
    """Test that an invalid api_key throws HERETransitUnauthorizedError."""
    aresponses.add(
        API_HOST,
        f"{API_VERSION}/{ROUTES_PATH}",
        "GET",
        aresponses.Response(
            text=load_json_fixture("invalid_key_response.json"),
            status=401,
            content_type="application/json",
        ),
    )
    async with aiohttp.ClientSession() as session:
        with pytest.raises(HERETransitUnauthorizedError):
            here_api = HERETransitApi(api_key="invalid", session=session)
            await here_api.route(
                origin=Place(latitude=50.12778680095556, longitude=8.582081794738771),
                destination=Place(
                    latitude=50.060940891421765, longitude=8.336477279663088
                ),
            )


@pytest.mark.asyncio
async def test_invalid_request(aresponses):
    """Test that a invalid request throws HERETransitError."""
    aresponses.add(
        API_HOST,
        f"{API_VERSION}/{ROUTES_PATH}",
        "GET",
        aresponses.Response(
            text=load_json_fixture("invalid_request_response.json"),
            status=400,
            content_type="application/json",
        ),
    )
    async with aiohttp.ClientSession() as session:
        with pytest.raises(HERETransitError) as error:
            here_api = HERETransitApi(api_key="key", session=session)
            await here_api.route(
                origin=Place(latitude=150.12778680095556, longitude=8.582081794738771),
                destination=Place(
                    latitude=50.060940891421765, longitude=8.336477279663088
                ),
            )
        assert "'origin': value is out of range" in str(error.value)


@pytest.mark.asyncio
async def test_no_route_found(aresponses):
    """Test that a no route found response throws HERETransitError."""
    aresponses.add(
        API_HOST,
        f"{API_VERSION}/{ROUTES_PATH}",
        "GET",
        aresponses.Response(
            text=load_json_fixture("no_route_found_response.json"),
            status=200,
            content_type="application/json",
        ),
    )
    async with aiohttp.ClientSession() as session:
        with pytest.raises(HERETransitError) as error:
            here_api = HERETransitApi(api_key="key", session=session)
            await here_api.route(
                origin=Place(latitude=150.12778680095556, longitude=8.582081794738771),
                destination=Place(
                    latitude=50.060940891421765, longitude=8.336477279663088
                ),
                changes=0,
            )
        assert "noRouteFound" in str(error.value)


def load_json_fixture(filename: str) -> str:
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, encoding="utf-8") as fptr:
        return fptr.read()

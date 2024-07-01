"""Tests for `here_transit.here_transit`."""

import os
from datetime import datetime

import aiohttp
import pytest

from here_transit.exceptions import (
    HERETransitDepartureArrivalTooCloseError,
    HERETransitError,
    HERETransitNoRouteFoundError,
    HERETransitNoTransitRouteFoundError,
    HERETransitTooManyRequestsError,
    HERETransitUnauthorizedError,
)
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
                destination=Place(latitude=50.060940891421765, longitude=8.336477279663088),
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
                destination=Place(latitude=50.060940891421765, longitude=8.336477279663088),
            )
        assert "'origin': value is out of range" in str(error.value)


@pytest.mark.asyncio
async def test_429_too_many_requests(aresponses):
    """Test that a invalid request throws HERETransitTooManyRequestsError."""
    aresponses.add(
        API_HOST,
        f"{API_VERSION}/{ROUTES_PATH}",
        "GET",
        aresponses.Response(
            text=load_json_fixture("too_many_requests_response.json"),
            status=429,
            content_type="application/json",
        ),
    )
    async with aiohttp.ClientSession() as session:
        with pytest.raises(HERETransitTooManyRequestsError) as error:
            here_api = HERETransitApi(api_key="key", session=session)
            await here_api.route(
                origin=Place(latitude=150.12778680095556, longitude=8.582081794738771),
                destination=Place(latitude=50.060940891421765, longitude=8.336477279663088),
            )
        assert "Rate limit for this service has been reached" in str(error.value)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "json_fixture,expected_exception,expected_exception_message",
    [
        (
            "noRouteFound_response.json",
            HERETransitNoRouteFoundError,
            ("Route between origin and destination " "is not possible given current input parameters"),
        ),
        (
            "noTransitRouteFound_response.json",
            HERETransitNoTransitRouteFoundError,
            "Transit routing between origin and destination is not possible",
        ),
        (
            "departureArrivalTooClose_response.json",
            HERETransitDepartureArrivalTooCloseError,
            "Departure and arrival locations are too close",
        ),
    ],
)
async def test_exceptions(aresponses, json_fixture, expected_exception, expected_exception_message):
    """Test correct HERETransitError are thrown."""
    aresponses.add(
        API_HOST,
        f"{API_VERSION}/{ROUTES_PATH}",
        "GET",
        aresponses.Response(
            text=load_json_fixture(json_fixture),
            status=200,
            content_type="application/json",
        ),
    )
    async with aiohttp.ClientSession() as session:
        with pytest.raises(expected_exception) as error:
            here_api = HERETransitApi(api_key="key", session=session)
            await here_api.route(
                origin=Place(latitude=150.12778680095556, longitude=8.582081794738771),
                destination=Place(latitude=50.060940891421765, longitude=8.336477279663088),
                changes=0,
            )
        assert expected_exception_message in str(error.value)


def load_json_fixture(filename: str) -> str:
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, encoding="utf-8") as fptr:
        return fptr.read()

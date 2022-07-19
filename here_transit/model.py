"""HERE Transit API models."""

from dataclasses import dataclass
from enum import Enum


class TransitMode(Enum):
    """Available TransportModes."""

    HIGHSPEED_TRAIN = "highSpeedTrain"
    INTERCITY_TRAIN = "intercityTrain"
    INTERREGIONAL_TRAIN = "interRegionalTrain"
    REGIONAL_TRAIN = "regionalTrain"
    CITY_TRAIN = "cityTrain"
    BUS = "bus"
    FERRY = "ferry"
    SUBWAY = "subway"
    LIGHT_RAIL = "lightRail"
    PRIVATE_BUS = "privateBus"
    INCLINED = "inclined"
    AERIAL = "aerial"
    BUS_RAPID = "busRapid"
    MONORAIL = "monorail"
    FLIGHT = "flight"
    SPACESHIP = "spaceship"


class UnitSystem(Enum):
    """Available UnitSystem Values."""

    METRIC = "metric"
    IMPERIAL = "imperial"


class Return(Enum):
    """Available Return Values."""

    INTERMEDIATE = "intermediate"
    FARES = "fares"
    POLYLINE = "polyline"
    ACTIONS = "actions"
    TRAVEL_SUMMARY = "travelSummary"
    INCIDENTS = "incidents"
    BOOKING_LINKS = "bookingLinks"


@dataclass
class Place:
    """Place for route requests."""

    latitude: float
    longitude: float

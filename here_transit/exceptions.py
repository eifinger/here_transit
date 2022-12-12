"""Exceptions for here_transit."""


class HERETransitError(Exception):
    """Generic HERE transit exception."""


class HERETransitConnectionError(HERETransitError):
    """HERE transit connection exception."""


class HERETransitUnauthorizedError(HERETransitError):
    """HERE transit unauthorized exception."""


class HERETransitTooManyRequestsError(HERETransitError):
    """HERE transit error wrapping HTTP 429"""


class HERETransitNoRouteFoundError(HERETransitError):
    """HERE transit noRouteFound exception."""


class HERETransitNoTransitRouteFoundError(HERETransitNoRouteFoundError):
    """HERE transit noTransitRouteFound exception."""


class HERETransitDepartureArrivalTooCloseError(HERETransitNoRouteFoundError):
    """HERE transit departureArrivalTooClose exception."""

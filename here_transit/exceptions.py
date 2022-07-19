"""Exceptions for here_transit."""


class HERETransitError(Exception):
    """Generic HERE transit exception."""


class HERETransitConnectionError(HERETransitError):
    """HERE transit connection exception."""


class HERETransitUnauthorizedError(HERETransitError):
    """HERE transit unauthorized exception."""

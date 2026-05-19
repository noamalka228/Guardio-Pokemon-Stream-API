"""
Custom exceptions for the proxy service.
"""


class NoMatchingRuleError(Exception):
    """
    Raised when no routing rule matches the incoming Pokémon.
    The client receives a 404 Not Found response.
    """
    pass


class DestinationTimeoutError(Exception):
    """
    Raised when the destination service does not respond within the timeout window.
    The client receives a 504 Gateway Timeout response.
    """
    pass

"""
Custom exceptions for the proxy service.
"""


class NoMatchingRuleError(Exception):
    """
    Raised when no routing rule matches the incoming Pokémon.
    The client receives a 404 Not Found response.
    """
    pass

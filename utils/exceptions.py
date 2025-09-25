"""Custom exceptions for the OSR Order GUI application."""


class OrderGUIException(Exception):
    """Base exception for Order GUI operations."""

    pass


class DatabaseConnectionError(OrderGUIException):
    """Raised when database connection fails."""

    pass


class ORBConnectionError(OrderGUIException):
    """Raised when CORBA ORB connection fails."""

    pass


class OrderValidationError(OrderGUIException):
    """Raised when order validation fails."""

    pass


class ConfigurationError(OrderGUIException):
    """Raised when configuration is invalid or missing."""

    pass

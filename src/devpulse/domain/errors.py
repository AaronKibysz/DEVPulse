class DevPulseError(Exception):
    """Base error for DevPulse."""


class IntegrationError(DevPulseError):
    """Raised when an integration cannot complete a request."""


class ValidationError(DevPulseError):
    """Raised when data from an external source is invalid."""

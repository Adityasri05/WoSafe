"""
WoSafe Core — Custom Exception Hierarchy
Structured exceptions with HTTP status codes and error codes.
"""

from typing import Any


class WoSafeException(Exception):
    """Base exception for all WoSafe errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(WoSafeException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(WoSafeException):
    """Raised when a user lacks required permissions."""

    def __init__(self, message: str = "Insufficient permissions", details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


class NotFoundError(WoSafeException):
    """Raised when a resource is not found."""

    def __init__(self, resource: str = "Resource", resource_id: str = "", details: dict[str, Any] | None = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details=details,
        )


class ValidationError(WoSafeException):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Validation failed", details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class ConflictError(WoSafeException):
    """Raised when a resource conflict occurs (e.g., duplicate)."""

    def __init__(self, message: str = "Resource conflict", details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT_ERROR",
            details=details,
        )


class RateLimitError(WoSafeException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded. Please try again later.", details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
        )


class ExternalServiceError(WoSafeException):
    """Raised when an external service call fails."""

    def __init__(self, service: str, message: str = "External service unavailable", details: dict[str, Any] | None = None):
        super().__init__(
            message=f"{service}: {message}",
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, **(details or {})},
        )


class EmergencyError(WoSafeException):
    """Raised for emergency-related failures — always critical priority."""

    def __init__(self, message: str = "Emergency system error", details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="EMERGENCY_ERROR",
            details=details,
        )

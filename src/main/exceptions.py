"""Custom exception classes for the application."""

from typing import Any


class AppException(Exception):
    """Base exception class for application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Any | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: The error message.
            status_code: HTTP status code.
            detail: Additional error details.
        """
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Exception raised for authentication errors."""

    def __init__(self, message: str = "Authentication failed", detail: Any | None = None) -> None:
        """Initialize authentication error.

        Args:
            message: The error message.
            detail: Additional error details.
        """
        super().__init__(message, status_code=401, detail=detail)


class AuthorizationError(AppException):
    """Exception raised for authorization errors."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        detail: Any | None = None,
    ) -> None:
        """Initialize authorization error.

        Args:
            message: The error message.
            detail: Additional error details.
        """
        super().__init__(message, status_code=403, detail=detail)


class NotFoundError(AppException):
    """Exception raised when a resource is not found."""

    def __init__(
        self,
        resource: str = "Resource",
        resource_id: int | str | None = None,
        detail: Any | None = None,
    ) -> None:
        """Initialize not found error.

        Args:
            resource: The type of resource that was not found.
            resource_id: The ID of the resource that was not found.
            detail: Additional error details.
        """
        message = (
            f"{resource} not found"
            if resource_id is None
            else f"{resource} with ID {resource_id} not found"
        )
        super().__init__(message, status_code=404, detail=detail)


class ValidationError(AppException):
    """Exception raised for validation errors."""

    def __init__(self, message: str = "Validation error", detail: Any | None = None) -> None:
        """Initialize validation error.

        Args:
            message: The error message.
            detail: Additional error details.
        """
        super().__init__(message, status_code=422, detail=detail)


class ConflictError(AppException):
    """Exception raised for resource conflicts."""

    def __init__(
        self,
        message: str = "Resource already exists",
        detail: Any | None = None,
    ) -> None:
        """Initialize conflict error.

        Args:
            message: The error message.
            detail: Additional error details.
        """
        super().__init__(message, status_code=409, detail=detail)


class DatabaseError(AppException):
    """Exception raised for database errors."""

    def __init__(
        self,
        message: str = "Database operation failed",
        detail: Any | None = None,
    ) -> None:
        """Initialize database error.

        Args:
            message: The error message.
            detail: Additional error details.
        """
        super().__init__(message, status_code=500, detail=detail)

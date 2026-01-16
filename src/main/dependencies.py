"""FastAPI dependencies for authentication and authorization."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.infra.db.models import User, get_db
from src.infra.db.utils import get_user_by_id, user_has_role
from src.main.exceptions import AuthenticationError, AuthorizationError, NotFoundError
from src.main.schemas import TokenData
from src.main.security import decode_access_token, verify_password

# HTTP Bearer token security scheme
security = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token from request header.
        db: Database session.

    Returns:
        Current authenticated user.

    Raises:
        AuthenticationError: If token is invalid or user not found.
    """
    token = credentials.credentials

    # Decode the JWT token
    payload = decode_access_token(token)
    if payload is None:
        raise AuthenticationError("Invalid or expired token")

    # Extract user ID from token
    user_id: int | None = payload.get("sub")
    if user_id is None:
        raise AuthenticationError("Invalid token payload")

    try:
        token_data = TokenData(user_id=user_id)
    except Exception as e:
        raise AuthenticationError("Invalid token data") from e

    # Get user from database
    try:
        user = get_user_by_id(db, user_id=token_data.user_id)
    except NotFoundError as e:
        raise AuthenticationError("User not found") from e

    if not user.is_active:
        raise AuthenticationError("User is inactive")

    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get the current active user.

    Args:
        current_user: Current authenticated user.

    Returns:
        Current active user.

    Raises:
        AuthenticationError: If user is not active.
    """
    if not current_user.is_active:
        raise AuthenticationError("User is inactive")
    return current_user


class RequirePermission:
    """Dependency class to check if user has required permission (role).

    Example usage:
        @router.get("/admin", dependencies=[Depends(RequirePermission("admin"))])
        async def admin_endpoint():
            return {"message": "Admin access granted"}
    """

    def __init__(self, permission_name: str) -> None:
        """Initialize the permission checker.

        Args:
            permission_name: The name of the required role/permission.
        """
        self._permission_name = permission_name

    async def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_db)],
    ) -> None:
        """Check if the current user has the required permission.

        Args:
            current_user: The current authenticated user.
            db: Database session.

        Raises:
            AuthorizationError: If user doesn't have the required permission.
        """
        if not user_has_role(db, current_user.id, self._permission_name):
            raise AuthorizationError(
                f"User does not have permission '{self._permission_name}'",
            )


class RequireAnyPermission:
    """Dependency class to check if user has any of the required permissions.

    Example usage:
        @router.get(
            "/resource",
            dependencies=[Depends(RequireAnyPermission(["admin", "moderator"]))]
        )
        async def resource_endpoint():
            return {"message": "Access granted"}
    """

    def __init__(self, permissions: list[str]) -> None:
        """Initialize the permission checker.

        Args:
            permissions: List of permission names (any one is sufficient).
        """
        self._permissions = permissions

    async def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_db)],
    ) -> None:
        """Check if the current user has any of the required permissions.

        Args:
            current_user: The current authenticated user.
            db: Database session.

        Raises:
            AuthorizationError: If user doesn't have any required permission.
        """
        for permission in self._permissions:
            if user_has_role(db, current_user.id, permission):
                return

        raise AuthorizationError(
            f"User does not have any of the required permissions: {', '.join(self._permissions)}",
        )


class RequireAllPermissions:
    """Dependency class to check if user has all required permissions.

    Example usage:
        @router.get(
            "/resource",
            dependencies=[Depends(RequireAllPermissions(["admin", "superuser"]))]
        )
        async def resource_endpoint():
            return {"message": "Access granted"}
    """

    def __init__(self, permissions: list[str]) -> None:
        """Initialize the permission checker.

        Args:
            permissions: List of permission names (all are required).
        """
        self._permissions = permissions

    async def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_db)],
    ) -> None:
        """Check if the current user has all required permissions.

        Args:
            current_user: The current authenticated user.
            db: Database session.

        Raises:
            AuthorizationError: If user doesn't have all required permissions.
        """
        missing_permissions = []
        for permission in self._permissions:
            if not user_has_role(db, current_user.id, permission):
                missing_permissions.append(permission)

        if missing_permissions:
            raise AuthorizationError(
                f"User is missing required permissions: {', '.join(missing_permissions)}",
            )


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """Authenticate a user with username and password.

    Args:
        db: Database session.
        username: Username to authenticate.
        password: Password to verify.

    Returns:
        User object if authentication successful, None otherwise.
    """
    from src.infra.db.utils import get_user_by_name

    user = get_user_by_name(db, username)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user

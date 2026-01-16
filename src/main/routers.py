"""Example endpoints demonstrating public and protected routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from src.infra.db.models import User
from src.main.dependencies import (
    RequireAllPermissions,
    RequireAnyPermission,
    RequirePermission,
    get_current_active_user,
)

router = APIRouter()


@router.get(
    "/public",
    tags=["Examples"],
    summary="Public endpoint",
    description="Public endpoint accessible to anyone without authentication",
)
async def public_endpoint() -> dict[str, str]:
    """Public endpoint that doesn't require authentication.

    Returns:
        Welcome message.
    """
    return {
        "message": "Hello from public endpoint!",
        "description": "This endpoint is accessible to everyone",
    }


@router.get(
    "/protected",
    dependencies=[Depends(RequirePermission("admin"))],
    tags=["Examples"],
    summary="Admin-only endpoint",
    description="Protected endpoint that requires admin role",
)
async def admin_only_endpoint(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """Admin-only protected endpoint.

    Args:
        current_user: Current authenticated user (must have admin role).

    Returns:
        Welcome message with user information.
    """
    return {
        "message": f"Hello {current_user.name}!",
        "description": "This endpoint requires admin permission",
        "user_id": current_user.id,
    }


@router.get(
    "/moderator",
    dependencies=[Depends(RequireAnyPermission(["admin", "moderator"]))],
    tags=["Examples"],
    summary="Moderator or Admin endpoint",
    description="Endpoint accessible to users with admin OR moderator role",
)
async def moderator_endpoint(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """Endpoint accessible to moderators or admins.

    Args:
        current_user: Current authenticated user (must have moderator or admin role).

    Returns:
        Welcome message with user information.
    """
    return {
        "message": f"Hello {current_user.name}!",
        "description": "This endpoint requires admin OR moderator permission",
        "user_id": current_user.id,
    }


@router.get(
    "/superuser",
    dependencies=[Depends(RequireAllPermissions(["admin", "superuser"]))],
    tags=["Examples"],
    summary="Super admin endpoint",
    description="Endpoint requiring BOTH admin AND superuser roles",
)
async def superuser_endpoint(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """Endpoint requiring both admin and superuser roles.

    Args:
        current_user: Current authenticated user (must have both admin and superuser roles).

    Returns:
        Welcome message with user information.
    """
    return {
        "message": f"Hello super admin {current_user.name}!",
        "description": "This endpoint requires BOTH admin AND superuser permissions",
        "user_id": current_user.id,
    }


@router.get(
    "/authenticated",
    tags=["Examples"],
    summary="Any authenticated user endpoint",
    description="Endpoint accessible to any authenticated user",
)
async def authenticated_endpoint(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """Endpoint accessible to any authenticated user.

    Args:
        current_user: Current authenticated user.

    Returns:
        Welcome message with user information.
    """
    return {
        "message": f"Hello {current_user.name}!",
        "description": "This endpoint requires authentication but no specific role",
        "user_id": current_user.id,
        "email": current_user.email,
    }

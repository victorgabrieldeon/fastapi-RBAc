"""User management endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.infra.db.models import User, get_db
from src.infra.db.utils import (
    assign_group_to_user,
    assign_role_to_user,
    create_user,
    delete_user,
    get_all_users,
    get_user_by_id,
    remove_group_from_user,
    remove_role_from_user,
    update_user,
)
from src.main.dependencies import RequirePermission, get_current_active_user
from src.main.schemas import (
    AssignGroupToUserRequest,
    AssignRoleToUserRequest,
    MessageResponse,
    UserCreate,
    UserDetailResponse,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Create a new user (requires admin permission)",
    dependencies=[Depends(RequirePermission("admin"))],
)
async def create_new_user(
    user_data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    """Create a new user.

    Args:
        user_data: User creation data.
        db: Database session dependency.

    Returns:
        Created user information.
    """
    user = create_user(
        db=db,
        name=user_data.name,
        password=user_data.password,
        email=user_data.email,
    )
    return UserResponse.model_validate(user)


@router.get(
    "",
    response_model=list[UserResponse],
    summary="List all users",
    description="Get list of all users with pagination (requires admin permission)",
    dependencies=[Depends(RequirePermission("admin"))],
)
async def list_users(
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of records to return",
    ),
) -> list[UserResponse]:
    """Get all users with pagination.

    Args:
        db: Database session dependency.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        List of users.
    """
    users = get_all_users(db, skip=skip, limit=limit)
    return [UserResponse.model_validate(user) for user in users]


@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    summary="Get user by ID",
    description="Get detailed user information including roles and groups",
)
async def get_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserDetailResponse:
    """Get user by ID.

    Args:
        user_id: User ID to retrieve.
        db: Database session dependency.
        current_user: Current authenticated user.

    Returns:
        Detailed user information.
    """
    user = get_user_by_id(db, user_id)
    return UserDetailResponse.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update user information (users can update themselves, admins can update anyone)",
)
async def update_user_info(
    user_id: int,
    user_data: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    """Update user information.

    Args:
        user_id: User ID to update.
        user_data: User update data.
        db: Database session dependency.
        current_user: Current authenticated user.

    Returns:
        Updated user information.
    """
    # Check if user is updating themselves or is an admin
    from src.infra.db.utils import user_has_role

    is_admin = user_has_role(db, current_user.id, "admin")
    if not is_admin and current_user.id != user_id:
        from src.main.exceptions import AuthorizationError

        raise AuthorizationError("You can only update your own profile")

    user = update_user(
        db=db,
        user_id=user_id,
        name=user_data.name,
        email=user_data.email,
        password=user_data.password,
    )
    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Delete user",
    description="Delete a user (requires admin permission)",
    dependencies=[Depends(RequirePermission("admin"))],
)
async def delete_user_endpoint(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    """Delete a user.

    Args:
        user_id: User ID to delete.
        db: Database session dependency.

    Returns:
        Success message.
    """
    delete_user(db, user_id)
    return MessageResponse(message=f"User with ID {user_id} deleted successfully")


@router.post(
    "/{user_id}/roles",
    response_model=UserDetailResponse,
    summary="Assign role to user",
    description="Assign a role directly to a user (requires admin permission)",
    dependencies=[Depends(RequirePermission("admin"))],
)
async def assign_role(
    user_id: int,
    role_data: AssignRoleToUserRequest,
    db: Annotated[Session, Depends(get_db)],
) -> UserDetailResponse:
    """Assign a role to a user.

    Args:
        user_id: User ID.
        role_data: Role assignment data.
        db: Database session dependency.

    Returns:
        Updated user with roles and groups.
    """
    user = assign_role_to_user(db, user_id, role_data.role_id)
    return UserDetailResponse.model_validate(user)


@router.delete(
    "/{user_id}/roles/{role_id}",
    response_model=UserDetailResponse,
    summary="Remove role from user",
    description="Remove a role from a user (requires admin permission)",
    dependencies=[Depends(RequirePermission("admin"))],
)
async def remove_role(
    user_id: int,
    role_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> UserDetailResponse:
    """Remove a role from a user.

    Args:
        user_id: User ID.
        role_id: Role ID to remove.
        db: Database session dependency.

    Returns:
        Updated user with roles and groups.
    """
    user = remove_role_from_user(db, user_id, role_id)
    return UserDetailResponse.model_validate(user)


@router.post(
    "/{user_id}/groups",
    response_model=UserDetailResponse,
    summary="Assign group to user",
    description="Assign a group to a user (requires admin permission)",
    dependencies=[Depends(RequirePermission("admin"))],
)
async def assign_group(
    user_id: int,
    group_data: AssignGroupToUserRequest,
    db: Annotated[Session, Depends(get_db)],
) -> UserDetailResponse:
    """Assign a group to a user.

    Args:
        user_id: User ID.
        group_data: Group assignment data.
        db: Database session dependency.

    Returns:
        Updated user with roles and groups.
    """
    user = assign_group_to_user(db, user_id, group_data.group_id)
    return UserDetailResponse.model_validate(user)


@router.delete(
    "/{user_id}/groups/{group_id}",
    response_model=UserDetailResponse,
    summary="Remove group from user",
    description="Remove a group from a user (requires admin permission)",
    dependencies=[Depends(RequirePermission("admin"))],
)
async def remove_group(
    user_id: int,
    group_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> UserDetailResponse:
    """Remove a group from a user.

    Args:
        user_id: User ID.
        group_id: Group ID to remove.
        db: Database session dependency.

    Returns:
        Updated user with roles and groups.
    """
    user = remove_group_from_user(db, user_id, group_id)
    return UserDetailResponse.model_validate(user)

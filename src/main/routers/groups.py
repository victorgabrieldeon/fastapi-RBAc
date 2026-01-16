"""Group management endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.infra.db.models import get_db
from src.infra.db.utils import (
    create_or_get_group,
    delete_group,
    get_all_groups,
    get_group_by_id,
    get_role_by_id,
)
from src.main.dependencies import RequirePermission
from src.main.schemas import GroupCreate, GroupResponse, MessageResponse

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.post(
    "",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new group",
    description="Create a new group with assigned roles (requires admin permission)",
    dependencies=[Depends(RequirePermission("admin"))],
)
async def create_group(
    group_data: GroupCreate,
    db: Annotated[Session, Depends(get_db)],
) -> GroupResponse:
    """Create a new group.

    Args:
        group_data: Group creation data with role IDs.
        db: Database session dependency.

    Returns:
        Created group information with roles.
    """
    # Get role objects from role IDs
    roles = [get_role_by_id(db, role_id) for role_id in group_data.role_ids]

    group = create_or_get_group(
        db=db,
        name=group_data.name,
        description=group_data.description,
        roles=roles,
    )
    return GroupResponse.model_validate(group)


@router.get(
    "",
    response_model=list[GroupResponse],
    summary="List all groups",
    description="Get list of all groups with their roles",
)
async def list_groups(
    db: Annotated[Session, Depends(get_db)],
) -> list[GroupResponse]:
    """Get all groups.

    Args:
        db: Database session dependency.

    Returns:
        List of all groups with their roles.
    """
    groups = get_all_groups(db)
    return [GroupResponse.model_validate(group) for group in groups]


@router.get(
    "/{group_id}",
    response_model=GroupResponse,
    summary="Get group by ID",
    description="Get detailed group information including roles",
)
async def get_group(
    group_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> GroupResponse:
    """Get group by ID.

    Args:
        group_id: Group ID to retrieve.
        db: Database session dependency.

    Returns:
        Group information with roles.
    """
    group = get_group_by_id(db, group_id)
    return GroupResponse.model_validate(group)


@router.delete(
    "/{group_id}",
    response_model=MessageResponse,
    summary="Delete group",
    description="Delete a group (requires admin permission)",
    dependencies=[Depends(RequirePermission("admin"))],
)
async def delete_group_endpoint(
    group_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    """Delete a group.

    Args:
        group_id: Group ID to delete.
        db: Database session dependency.

    Returns:
        Success message.
    """
    delete_group(db, group_id)
    return MessageResponse(message=f"Group with ID {group_id} deleted successfully")

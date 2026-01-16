"""Role management endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.infra.db.models import get_db
from src.infra.db.utils import (
    create_or_get_role,
    delete_role,
    get_all_roles,
    get_role_by_id,
)
from src.main.dependencies import RequirePermission
from src.main.schemas import MessageResponse, RoleCreate, RoleResponse

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new role",
    description="Create a new role (requires admin permission)",
    dependencies=[Depends(RequirePermission("admin"))],
)
async def create_role(
    role_data: RoleCreate,
    db: Annotated[Session, Depends(get_db)],
) -> RoleResponse:
    """Create a new role.

    Args:
        role_data: Role creation data.
        db: Database session dependency.

    Returns:
        Created role information.
    """
    role = create_or_get_role(
        db=db,
        name=role_data.name,
        description=role_data.description,
    )
    return RoleResponse.model_validate(role)


@router.get(
    "",
    response_model=list[RoleResponse],
    summary="List all roles",
    description="Get list of all available roles",
)
async def list_roles(
    db: Annotated[Session, Depends(get_db)],
) -> list[RoleResponse]:
    """Get all roles.

    Args:
        db: Database session dependency.

    Returns:
        List of all roles.
    """
    roles = get_all_roles(db)
    return [RoleResponse.model_validate(role) for role in roles]


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Get role by ID",
    description="Get detailed role information",
)
async def get_role(
    role_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> RoleResponse:
    """Get role by ID.

    Args:
        role_id: Role ID to retrieve.
        db: Database session dependency.

    Returns:
        Role information.
    """
    role = get_role_by_id(db, role_id)
    return RoleResponse.model_validate(role)


@router.delete(
    "/{role_id}",
    response_model=MessageResponse,
    summary="Delete role",
    description="Delete a role (requires admin permission)",
    dependencies=[Depends(RequirePermission("admin"))],
)
async def delete_role_endpoint(
    role_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    """Delete a role.

    Args:
        role_id: Role ID to delete.
        db: Database session dependency.

    Returns:
        Success message.
    """
    delete_role(db, role_id)
    return MessageResponse(message=f"Role with ID {role_id} deleted successfully")

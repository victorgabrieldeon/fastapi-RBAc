"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Authentication Schemas
# ============================================================================


class Token(BaseModel):
    """JWT token response schema."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Token payload data schema."""

    user_id: int | None = Field(default=None, description="User ID from token")


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=6, description="Password")


# ============================================================================
# User Schemas
# ============================================================================


class UserBase(BaseModel):
    """Base user schema with common fields."""

    name: str = Field(..., min_length=3, max_length=50, description="User name")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=6, description="User password")
    email: str | None = Field(default=None, description="User email")


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    name: str | None = Field(default=None, min_length=3, max_length=50)
    email: str | None = Field(default=None)
    password: str | None = Field(default=None, min_length=6)


class UserResponse(UserBase):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="User ID")
    email: str | None = Field(default=None, description="User email")


class UserDetailResponse(UserResponse):
    """Detailed user response including roles and groups."""

    roles: list["RoleResponse"] = Field(default_factory=list, description="User roles")
    groups: list["GroupResponse"] = Field(
        default_factory=list,
        description="User groups",
    )


# ============================================================================
# Role Schemas
# ============================================================================


class RoleBase(BaseModel):
    """Base role schema with common fields."""

    name: str = Field(..., min_length=2, max_length=50, description="Role name")
    description: str = Field(..., max_length=200, description="Role description")


class RoleCreate(RoleBase):
    """Schema for creating a new role."""


class RoleUpdate(BaseModel):
    """Schema for updating role information."""

    name: str | None = Field(default=None, min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=200)


class RoleResponse(RoleBase):
    """Schema for role response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Role ID")


# ============================================================================
# Group Schemas
# ============================================================================


class GroupBase(BaseModel):
    """Base group schema with common fields."""

    name: str = Field(..., min_length=2, max_length=50, description="Group name")
    description: str = Field(..., max_length=200, description="Group description")


class GroupCreate(GroupBase):
    """Schema for creating a new group."""

    role_ids: list[int] = Field(default_factory=list, description="List of role IDs")


class GroupUpdate(BaseModel):
    """Schema for updating group information."""

    name: str | None = Field(default=None, min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=200)
    role_ids: list[int] | None = Field(default=None, description="List of role IDs")


class GroupResponse(GroupBase):
    """Schema for group response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Group ID")
    roles: list[RoleResponse] = Field(
        default_factory=list,
        description="Group roles",
    )


# ============================================================================
# Assignment Schemas
# ============================================================================


class AssignRoleToUserRequest(BaseModel):
    """Schema for assigning a role to a user."""

    role_id: int = Field(..., description="Role ID to assign")


class AssignGroupToUserRequest(BaseModel):
    """Schema for assigning a group to a user."""

    group_id: int = Field(..., description="Group ID to assign")


# ============================================================================
# Generic Response Schemas
# ============================================================================


class MessageResponse(BaseModel):
    """Generic message response schema."""

    message: str = Field(..., description="Response message")
    detail: str | None = Field(default=None, description="Additional details")


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: str | None = Field(default=None, description="Additional error details")

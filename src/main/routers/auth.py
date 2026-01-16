"""Authentication endpoints for user login and token management."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.infra.db.models import get_db
from src.main.config import get_settings
from src.main.dependencies import authenticate_user, get_current_active_user
from src.main.exceptions import AuthenticationError
from src.main.schemas import LoginRequest, MessageResponse, Token, UserResponse
from src.main.security import create_access_token

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Authenticate user with username and password to receive JWT token",
)
async def login(
    login_data: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """Login endpoint to authenticate users and return JWT token.

    Args:
        login_data: Login credentials (username and password).
        db: Database session dependency.

    Returns:
        JWT access token and token type.

    Raises:
        AuthenticationError: If credentials are invalid.
    """
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise AuthenticationError("Incorrect username or password")

    if not user.is_active:
        raise AuthenticationError("User account is inactive")

    # Create JWT token with user ID as subject
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get information about the currently authenticated user",
)
async def get_current_user_info(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
) -> UserResponse:
    """Get current authenticated user information.

    Args:
        current_user: Current authenticated user from JWT token.

    Returns:
        Current user information.
    """
    return current_user


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="User logout",
    description="Logout user (client should delete the token)",
)
async def logout(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
) -> MessageResponse:
    """Logout endpoint (stateless - client should delete token).

    Args:
        current_user: Current authenticated user.

    Returns:
        Logout success message.
    """
    return MessageResponse(
        message="Logout successful",
        detail="Please delete your access token on the client side",
    )

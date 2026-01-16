"""Database utility functions for RBAC operations."""

import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.infra.db.models import Group, Role, User
from src.main.exceptions import ConflictError, DatabaseError, NotFoundError
from src.main.security import get_password_hash

logger = logging.getLogger(__name__)


# ============================================================================
# User Operations
# ============================================================================


def create_user(
    db: Session,
    name: str,
    password: str,
    email: str | None = None,
    groups: list[Group] | None = None,
    roles: list[Role] | None = None,
) -> User:
    """Create a new user with password hashing.

    Args:
        db: Database session.
        name: Username.
        password: Plain text password.
        email: Optional user email.
        groups: Optional list of groups to assign.
        roles: Optional list of roles to assign.

    Returns:
        Created user object.

    Raises:
        ConflictError: If username or email already exists.
        DatabaseError: If database operation fails.
    """
    try:
        # Check if user with same name already exists
        existing_user = db.query(User).filter(User.name == name).first()
        if existing_user:
            raise ConflictError(f"User with name '{name}' already exists")

        # Check if email is provided and already exists
        if email:
            existing_email = db.query(User).filter(User.email == email).first()
            if existing_email:
                raise ConflictError(f"User with email '{email}' already exists")

        hashed_password = get_password_hash(password)
        user = User(
            name=name,
            email=email,
            hashed_password=hashed_password,
            groups=groups or [],
            roles=roles or [],
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"User created successfully: {user.name} (ID: {user.id})")
        return user

    except (ConflictError, DatabaseError):
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating user: {e}")
        raise ConflictError("User already exists") from e
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating user: {e}")
        raise DatabaseError("Failed to create user") from e


def get_user_by_id(db: Session, user_id: int) -> User:
    """Get a user by ID.

    Args:
        db: Database session.
        user_id: User ID to search for.

    Returns:
        User object if found.

    Raises:
        NotFoundError: If user is not found.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise NotFoundError("User", user_id)
    return user


def get_user_by_name(db: Session, name: str) -> User | None:
    """Get a user by name.

    Args:
        db: Database session.
        name: Username to search for.

    Returns:
        User object if found, None otherwise.
    """
    return db.query(User).filter(User.name == name).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Get a user by email.

    Args:
        db: Database session.
        email: Email to search for.

    Returns:
        User object if found, None otherwise.
    """
    return db.query(User).filter(User.email == email).first()


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Get all users with pagination.

    Args:
        db: Database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        List of users.
    """
    return db.query(User).offset(skip).limit(limit).all()


def update_user(
    db: Session,
    user_id: int,
    name: str | None = None,
    email: str | None = None,
    password: str | None = None,
) -> User:
    """Update user information.

    Args:
        db: Database session.
        user_id: User ID to update.
        name: New username (optional).
        email: New email (optional).
        password: New password (optional).

    Returns:
        Updated user object.

    Raises:
        NotFoundError: If user is not found.
        ConflictError: If new username or email already exists.
        DatabaseError: If database operation fails.
    """
    try:
        user = get_user_by_id(db, user_id)

        if name and name != user.name:
            existing = db.query(User).filter(User.name == name).first()
            if existing:
                raise ConflictError(f"User with name '{name}' already exists")
            user.name = name

        if email and email != user.email:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                raise ConflictError(f"User with email '{email}' already exists")
            user.email = email

        if password:
            user.hashed_password = get_password_hash(password)

        db.commit()
        db.refresh(user)
        logger.info(f"User updated successfully: {user.name} (ID: {user.id})")
        return user

    except (NotFoundError, ConflictError, DatabaseError):
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating user: {e}")
        raise DatabaseError("Failed to update user") from e


def delete_user(db: Session, user_id: int) -> None:
    """Delete a user.

    Args:
        db: Database session.
        user_id: User ID to delete.

    Raises:
        NotFoundError: If user is not found.
        DatabaseError: If database operation fails.
    """
    try:
        user = get_user_by_id(db, user_id)
        db.delete(user)
        db.commit()
        logger.info(f"User deleted successfully: {user.name} (ID: {user.id})")

    except (NotFoundError, DatabaseError):
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting user: {e}")
        raise DatabaseError("Failed to delete user") from e


# ============================================================================
# Role Operations
# ============================================================================


def create_or_get_role(db: Session, name: str, description: str) -> Role:
    """Create a new role or get existing one by name.

    Args:
        db: Database session.
        name: Role name.
        description: Role description.

    Returns:
        Role object.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        role = db.query(Role).filter(Role.name == name).first()
        if role:
            return role

        role = Role(name=name, description=description)
        db.add(role)
        db.commit()
        db.refresh(role)
        logger.info(f"Role created successfully: {role.name} (ID: {role.id})")
        return role

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating role: {e}")
        raise DatabaseError("Failed to create role") from e


def get_role_by_id(db: Session, role_id: int) -> Role:
    """Get a role by ID.

    Args:
        db: Database session.
        role_id: Role ID to search for.

    Returns:
        Role object if found.

    Raises:
        NotFoundError: If role is not found.
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise NotFoundError("Role", role_id)
    return role


def get_role_by_name(db: Session, name: str) -> Role | None:
    """Get a role by name.

    Args:
        db: Database session.
        name: Role name to search for.

    Returns:
        Role object if found, None otherwise.
    """
    return db.query(Role).filter(Role.name == name).first()


def get_all_roles(db: Session) -> list[Role]:
    """Get all roles.

    Args:
        db: Database session.

    Returns:
        List of all roles.
    """
    return db.query(Role).all()


def delete_role(db: Session, role_id: int) -> None:
    """Delete a role.

    Args:
        db: Database session.
        role_id: Role ID to delete.

    Raises:
        NotFoundError: If role is not found.
        DatabaseError: If database operation fails.
    """
    try:
        role = get_role_by_id(db, role_id)
        db.delete(role)
        db.commit()
        logger.info(f"Role deleted successfully: {role.name} (ID: {role.id})")

    except (NotFoundError, DatabaseError):
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting role: {e}")
        raise DatabaseError("Failed to delete role") from e


# ============================================================================
# Group Operations
# ============================================================================


def create_or_get_group(
    db: Session,
    name: str,
    description: str,
    roles: list[Role] | None = None,
) -> Group:
    """Create a new group or get existing one by name.

    Args:
        db: Database session.
        name: Group name.
        description: Group description.
        roles: Optional list of roles to assign.

    Returns:
        Group object.

    Raises:
        DatabaseError: If database operation fails.
    """
    try:
        group = db.query(Group).filter(Group.name == name).first()
        if group:
            return group

        group = Group(name=name, description=description, roles=roles or [])
        db.add(group)
        db.commit()
        db.refresh(group)
        logger.info(f"Group created successfully: {group.name} (ID: {group.id})")
        return group

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating group: {e}")
        raise DatabaseError("Failed to create group") from e


def get_group_by_id(db: Session, group_id: int) -> Group:
    """Get a group by ID.

    Args:
        db: Database session.
        group_id: Group ID to search for.

    Returns:
        Group object if found.

    Raises:
        NotFoundError: If group is not found.
    """
    group = db.query(Group).filter(Group.id == group_id).first()
    if group is None:
        raise NotFoundError("Group", group_id)
    return group


def get_all_groups(db: Session) -> list[Group]:
    """Get all groups.

    Args:
        db: Database session.

    Returns:
        List of all groups.
    """
    return db.query(Group).all()


def delete_group(db: Session, group_id: int) -> None:
    """Delete a group.

    Args:
        db: Database session.
        group_id: Group ID to delete.

    Raises:
        NotFoundError: If group is not found.
        DatabaseError: If database operation fails.
    """
    try:
        group = get_group_by_id(db, group_id)
        db.delete(group)
        db.commit()
        logger.info(f"Group deleted successfully: {group.name} (ID: {group.id})")

    except (NotFoundError, DatabaseError):
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting group: {e}")
        raise DatabaseError("Failed to delete group") from e


# ============================================================================
# Permission Checking
# ============================================================================


def user_has_role(db: Session, user_id: int, role_name: str) -> bool:
    """Check if a user has a specific role.

    The user can have the role either directly assigned or through a group.

    Args:
        db: Database session.
        user_id: User ID to check.
        role_name: Role name to verify.

    Returns:
        True if user has the role, False otherwise.
    """
    try:
        query = (
            db.query(User)
            .filter(
                (User.id == user_id)
                & (
                    User.roles.any(Role.name == role_name)
                    | User.groups.any(Group.roles.any(Role.name == role_name))
                ),
            )
            .exists()
        )
        return db.query(query).scalar()

    except SQLAlchemyError as e:
        logger.error(f"Database error checking user role: {e}")
        return False


# ============================================================================
# Assignment Operations
# ============================================================================


def assign_role_to_user(db: Session, user_id: int, role_id: int) -> User:
    """Assign a role directly to a user.

    Args:
        db: Database session.
        user_id: User ID.
        role_id: Role ID to assign.

    Returns:
        Updated user object.

    Raises:
        NotFoundError: If user or role is not found.
        ConflictError: If role is already assigned.
        DatabaseError: If database operation fails.
    """
    try:
        user = get_user_by_id(db, user_id)
        role = get_role_by_id(db, role_id)

        if role in user.roles:
            raise ConflictError(f"Role '{role.name}' is already assigned to user")

        user.roles.append(role)
        db.commit()
        db.refresh(user)
        logger.info(f"Role '{role.name}' assigned to user '{user.name}'")
        return user

    except (NotFoundError, ConflictError, DatabaseError):
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error assigning role to user: {e}")
        raise DatabaseError("Failed to assign role to user") from e


def remove_role_from_user(db: Session, user_id: int, role_id: int) -> User:
    """Remove a role from a user.

    Args:
        db: Database session.
        user_id: User ID.
        role_id: Role ID to remove.

    Returns:
        Updated user object.

    Raises:
        NotFoundError: If user, role is not found, or role is not assigned.
        DatabaseError: If database operation fails.
    """
    try:
        user = get_user_by_id(db, user_id)
        role = get_role_by_id(db, role_id)

        if role not in user.roles:
            raise NotFoundError(f"Role '{role.name}' is not assigned to user")

        user.roles.remove(role)
        db.commit()
        db.refresh(user)
        logger.info(f"Role '{role.name}' removed from user '{user.name}'")
        return user

    except (NotFoundError, DatabaseError):
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error removing role from user: {e}")
        raise DatabaseError("Failed to remove role from user") from e


def assign_group_to_user(db: Session, user_id: int, group_id: int) -> User:
    """Assign a group to a user.

    Args:
        db: Database session.
        user_id: User ID.
        group_id: Group ID to assign.

    Returns:
        Updated user object.

    Raises:
        NotFoundError: If user or group is not found.
        ConflictError: If group is already assigned.
        DatabaseError: If database operation fails.
    """
    try:
        user = get_user_by_id(db, user_id)
        group = get_group_by_id(db, group_id)

        if group in user.groups:
            raise ConflictError(f"Group '{group.name}' is already assigned to user")

        user.groups.append(group)
        db.commit()
        db.refresh(user)
        logger.info(f"Group '{group.name}' assigned to user '{user.name}'")
        return user

    except (NotFoundError, ConflictError, DatabaseError):
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error assigning group to user: {e}")
        raise DatabaseError("Failed to assign group to user") from e


def remove_group_from_user(db: Session, user_id: int, group_id: int) -> User:
    """Remove a group from a user.

    Args:
        db: Database session.
        user_id: User ID.
        group_id: Group ID to remove.

    Returns:
        Updated user object.

    Raises:
        NotFoundError: If user, group is not found, or group is not assigned.
        DatabaseError: If database operation fails.
    """
    try:
        user = get_user_by_id(db, user_id)
        group = get_group_by_id(db, group_id)

        if group not in user.groups:
            raise NotFoundError(f"Group '{group.name}' is not assigned to user")

        user.groups.remove(group)
        db.commit()
        db.refresh(user)
        logger.info(f"Group '{group.name}' removed from user '{user.name}'")
        return user

    except (NotFoundError, DatabaseError):
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error removing group from user: {e}")
        raise DatabaseError("Failed to remove group from user") from e

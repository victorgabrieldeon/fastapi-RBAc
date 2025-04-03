from fastapi import HTTPException

from src.infra.db.models import Group, Role, User, session


def create_user(
    name: str,
    groups: list[Group] | None = None,
    roles: list[Role] | None = None,
) -> User:
    """Create a new user."""
    user = User(name=name, groups=groups or [], roles=roles or [])
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_or_get_role(name: str, description: str) -> Role:
    """Create a new role."""
    role = session.query(Role).filter(Role.name == name).first()

    if role:
        return role

    role = Role(name=name, description=description)
    session.add(role)
    session.commit()
    session.refresh(role)
    return role


def create_or_get_group(name: str, description: str, roles: list[Role]) -> Group:
    """Create a new group."""
    group = session.query(Group).filter(Group.name == name).first()

    if group:
        return group

    group = Group(name=name, description=description, roles=roles)
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


def get_user_by_id(user_id: int) -> User:
    """Get a user by ID."""
    user = session.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} not found",
        )

    return user


def user_has_role(user_id: int, role_name: str) -> bool:
    """Check if a user has a specific role."""
    query = (
        session.query(User)
        .filter(
            (User.id == user_id)
            & (
                User.roles.any(Role.name == role_name)
                | User.groups.any(Group.roles.any(Role.name == role_name))
            ),
        )
        .exists()
    )

    return session.query(query).scalar()

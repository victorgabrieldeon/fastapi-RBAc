from fastapi import FastAPI

from src.infra.db.utils import (
    create_or_get_group,
    create_or_get_role,
    create_user,
)

from .routers import router

role = create_or_get_role(name="admin", description="Administrator")
group = create_or_get_group(name="admin", description="Administrator", roles=[role])
admin_user = create_user(name="admin", groups=[group])
basic_user = create_user(name="basic")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="FastAPI RBAC",
        description="FastAPI RBAC is a simple role-based"
        " access control system for FastAPI.",
    )

    print(f"Admin user created: ID={admin_user.id}")  # noqa: T201
    print(f"Basic user created: ID={basic_user.id}")  # noqa: T201

    app.include_router(router)

    return app


app = create_app()

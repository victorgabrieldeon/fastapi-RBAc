"""FastAPI RBAC application factory and configuration."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.infra.db.models import SessionLocal, get_db
from src.infra.db.utils import create_or_get_group, create_or_get_role, create_user
from src.main.config import get_settings
from src.main.exceptions import AppException
from src.main.logging_config import setup_logging
from src.main.routers import auth, groups, roles, users
from src.main.routers import router as examples_router

settings = get_settings()
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    # Setup logging first
    setup_logging()

    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "A robust Role-Based Access Control (RBAC) system built with FastAPI. "
            "Features JWT authentication, comprehensive CRUD operations, "
            "and flexible permission management through roles and groups."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register exception handlers
    register_exception_handlers(app)

    # Include routers
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(roles.router)
    app.include_router(groups.router)
    app.include_router(examples_router)

    # Initialize database with sample data on startup
    @app.on_event("startup")
    async def startup_event() -> None:
        """Initialize database with sample data on application startup."""
        logger.info("Application starting up...")
        logger.info(f"Debug mode: {settings.debug}")
        logger.info(f"Database URL: {settings.database_url}")

        # Initialize sample data
        initialize_sample_data()

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        """Clean up resources on application shutdown."""
        logger.info("Application shutting down...")
        SessionLocal.remove()

    return app


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers for the application.

    Args:
        app: FastAPI application instance.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ) -> JSONResponse:
        """Handle custom application exceptions.

        Args:
            request: The incoming request.
            exc: The application exception.

        Returns:
            JSON response with error details.
        """
        logger.error(
            f"Application error: {exc.message} - Path: {request.url.path}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "detail": exc.detail,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle request validation errors.

        Args:
            request: The incoming request.
            exc: The validation error.

        Returns:
            JSON response with validation error details.
        """
        logger.warning(
            f"Validation error: {exc.errors()} - Path: {request.url.path}",
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "ValidationError",
                "message": "Request validation failed",
                "detail": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unexpected exceptions.

        Args:
            request: The incoming request.
            exc: The exception.

        Returns:
            JSON response with generic error message.
        """
        logger.error(
            f"Unexpected error: {exc} - Path: {request.url.path}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "detail": str(exc) if settings.debug else None,
            },
        )


def initialize_sample_data() -> None:
    """Initialize database with sample roles, groups, and users."""
    db = SessionLocal()
    try:
        logger.info("Initializing sample data...")

        # Create roles
        admin_role = create_or_get_role(
            db,
            name="admin",
            description="Administrator with full access",
        )
        moderator_role = create_or_get_role(
            db,
            name="moderator",
            description="Moderator with limited administrative access",
        )
        user_role = create_or_get_role(
            db,
            name="user",
            description="Regular user with basic access",
        )
        superuser_role = create_or_get_role(
            db,
            name="superuser",
            description="Super administrator with all permissions",
        )

        logger.info("Sample roles created: admin, moderator, user, superuser")

        # Create groups
        admin_group = create_or_get_group(
            db,
            name="admins",
            description="Administrator group",
            roles=[admin_role],
        )
        moderator_group = create_or_get_group(
            db,
            name="moderators",
            description="Moderator group",
            roles=[moderator_role],
        )
        user_group = create_or_get_group(
            db,
            name="users",
            description="Regular users group",
            roles=[user_role],
        )

        logger.info("Sample groups created: admins, moderators, users")

        # Create sample users
        try:
            admin_user = create_user(
                db,
                name="admin",
                password="admin123",
                email="admin@example.com",
                groups=[admin_group],
            )
            logger.info(
                f"✓ Admin user created - Username: admin, Password: admin123, "
                f"ID: {admin_user.id}",
            )
        except Exception as e:
            logger.info(f"Admin user already exists: {e}")

        try:
            moderator_user = create_user(
                db,
                name="moderator",
                password="mod123",
                email="moderator@example.com",
                groups=[moderator_group],
            )
            logger.info(
                f"✓ Moderator user created - Username: moderator, Password: mod123, "
                f"ID: {moderator_user.id}",
            )
        except Exception as e:
            logger.info(f"Moderator user already exists: {e}")

        try:
            basic_user = create_user(
                db,
                name="user",
                password="user123",
                email="user@example.com",
                groups=[user_group],
            )
            logger.info(
                f"✓ Regular user created - Username: user, Password: user123, "
                f"ID: {basic_user.id}",
            )
        except Exception as e:
            logger.info(f"Regular user already exists: {e}")

        try:
            super_admin = create_user(
                db,
                name="superadmin",
                password="super123",
                email="superadmin@example.com",
                roles=[admin_role, superuser_role],
            )
            logger.info(
                f"✓ Super admin user created - Username: superadmin, Password: super123, "
                f"ID: {super_admin.id}",
            )
        except Exception as e:
            logger.info(f"Super admin user already exists: {e}")

        logger.info("Sample data initialization complete!")
        logger.info("=" * 80)
        logger.info("Test Credentials:")
        logger.info("  Admin: username='admin', password='admin123'")
        logger.info("  Moderator: username='moderator', password='mod123'")
        logger.info("  User: username='user', password='user123'")
        logger.info("  Super Admin: username='superadmin', password='super123'")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Error initializing sample data: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


# Create the FastAPI app instance
app = create_app()

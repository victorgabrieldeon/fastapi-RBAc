from fastapi import APIRouter, Depends

from src.main.auth import RequirePermission

router = APIRouter()


@router.get(
    "/protected",
    dependencies=[Depends(RequirePermission("admin"))],
    tags=["Protected"],
)
async def protected() -> dict[str, str]:
    """Protected endpoint."""
    return {"Hello": "World"}


@router.get("/public", tags=["Public"])
async def public() -> dict[str, str]:
    """Public endpoint."""
    return {"Hello": "Public World"}

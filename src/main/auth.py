from fastapi import HTTPException, Query

from src.infra.db.utils import get_user_by_id, user_has_role


class RequirePermission:
    def __init__(self, permission_name: str) -> None:
        self._permission_name = permission_name

    async def __call__(self, user_id: int = Query()) -> None:
        """Check if the user has the required permission."""
        try:
            get_user_by_id(user_id)

        except HTTPException:
            raise HTTPException(  # noqa: B904
                status_code=401,
                detail="Token is invalid or expired",
            )

        if not user_has_role(
            user_id=user_id,
            role_name=self._permission_name,
        ):
            raise HTTPException(
                status_code=403,
                detail=f"User does not have permission {self._permission_name}",
            )

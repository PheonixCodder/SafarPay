"""Role-based permission system.

Usage:
    @router.get("/admin-only")
    async def admin_route(user = Depends(require_role(Permission.ADMIN))):
        ...
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated

from fastapi import Depends, HTTPException, status

from .dependencies import get_current_user
from .jwt import TokenPayload


class Permission(str, Enum):
    PASSENGER = "passenger"
    DRIVER = "driver"
    ADMIN = "admin"


def require_role(*roles: Permission):
    """Dependency factory that enforces role-based access control.

    Returns the verified TokenPayload so callers can use it directly.
    Raises HTTP 403 if the authenticated user's role is not in the allowed list.
    """
    async def _check(
        user: Annotated[TokenPayload, Depends(get_current_user)]
    ) -> TokenPayload:
        if user.role not in [r.value for r in roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in roles]}",
            )
        return user

    return _check

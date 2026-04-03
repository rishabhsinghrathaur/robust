import os
import secrets
from typing import Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel


Role = Literal["viewer", "operator", "admin"]
security = HTTPBearer(auto_error=False)


class AuthContext(BaseModel):
    token_name: str
    role: Role


def _configured_tokens() -> dict[str, Role]:
    return {
        os.getenv("ROBUST_VIEWER_TOKEN", "viewer-dev-token"): "viewer",
        os.getenv("ROBUST_OPERATOR_TOKEN", "operator-dev-token"): "operator",
        os.getenv("ROBUST_ADMIN_TOKEN", "admin-dev-token"): "admin",
    }


def require_role(minimum_role: Role):
    rank = {"viewer": 1, "operator": 2, "admin": 3}

    def dependency(
        credentials: HTTPAuthorizationCredentials | None = Depends(security),
    ) -> AuthContext:
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

        token_map = _configured_tokens()
        matched_role = next(
            (role for token, role in token_map.items() if secrets.compare_digest(credentials.credentials, token)),
            None,
        )
        if matched_role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        if rank[matched_role] < rank[minimum_role]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{minimum_role} role required")
        return AuthContext(token_name=f"{matched_role}-token", role=matched_role)

    return dependency


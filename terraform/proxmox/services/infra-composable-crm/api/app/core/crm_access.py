"""Validate GoTrue JWTs and derive CRM entitlements from signed app metadata."""
from dataclasses import dataclass
from os import getenv
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

EXPENSE_PARTITIONS = frozenset({"SHARED", "Nucleo_tecnologico", "Mailerblend"})
PROJECTS = frozenset({"form_entries", "smart_management", "linkedin_sourcing"})
ROLE_MODES = frozenset({"viewer", "editor"})


@dataclass(frozen=True)
class CRMAccess:
    subject: UUID
    is_admin: bool
    project_roles: dict[str, str]
    expense_roles: frozenset[tuple[str, str]]

    def allows_project(self, project: str, *, write: bool = False) -> bool:
        role = self.project_roles.get(project)
        return project in PROJECTS and (
            self.is_admin or role == "editor" or (role == "viewer" and not write)
        )

    def expense_partitions(self, *, write: bool = False) -> frozenset[str]:
        if self.is_admin:
            return EXPENSE_PARTITIONS
        partitions = frozenset(
            partition for mode, partition in self.expense_roles if not write or mode == "editor"
        )
        if partitions and not write:
            return partitions | {"SHARED"}
        return partitions

    def require_expense_partition(self, partition: str, *, write: bool = False) -> None:
        if partition not in self.expense_partitions(write=write):
            raise HTTPException(status_code=403, detail="Expense partition forbidden")


def validate_gotrue_token(token: str, *, key: str, issuer: str) -> CRMAccess:
    try:
        claims = jwt.decode(
            token,
            key,
            algorithms=["HS256"],
            issuer=issuer,
            audience="authenticated",
            options={"require": ["exp", "iss", "aud", "sub"]},
        )
        subject = UUID(claims["sub"])
        if claims.get("role") != "authenticated":
            raise ValueError("Expected a user token")
        metadata = claims.get("app_metadata") or {}
        project_roles = metadata.get("project_roles", {})
        expense_roles = metadata.get("expense_roles", [])
        if not isinstance(project_roles, dict) or not isinstance(expense_roles, list):
            raise ValueError("Invalid grants")
        if any(
            project not in PROJECTS or not isinstance(mode, str) or mode not in ROLE_MODES
            for project, mode in project_roles.items()
        ):
            raise ValueError("Invalid project role")
        parsed = set()
        for role in expense_roles:
            mode, _, partition = role.partition(":")
            if mode not in ROLE_MODES or partition not in EXPENSE_PARTITIONS:
                raise ValueError("Invalid expense role")
            parsed.add((mode, partition))
        return CRMAccess(subject, metadata.get("crm_role") == "admin", project_roles, frozenset(parsed))
    except (jwt.PyJWTError, ValueError, TypeError, AttributeError):
        raise HTTPException(status_code=401, detail="Invalid CRM session") from None


bearer = HTTPBearer(auto_error=False)


def require_crm_access(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> CRMAccess:
    key = getenv("CRM_AUTH_JWT_SECRET")
    issuer = getenv("CRM_AUTH_ISSUER")
    if not credentials or not key or not issuer:
        raise HTTPException(status_code=401, detail="CRM session required")
    return validate_gotrue_token(credentials.credentials, key=key, issuer=issuer)


def crm_auth_enabled() -> bool:
    return getenv("CRM_AUTH_ENABLED") == "1"

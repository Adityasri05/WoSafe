"""
WoSafe Services — Audit Service
Centralized security compliance, activity monitoring, and audit log generation.
"""

from uuid import UUID
from fastapi import Request

from app.core.exceptions import NotFoundError
from app.repositories import AuditLogRepository
from app.models import AuditLog


class AuditService:
    """Handles platform security auditing, compliance, and user activity logging."""

    def __init__(self, db):
        self.db = db
        self.audit_repo = AuditLogRepository(db)

    async def log_activity(
        self,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        user_id: UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: dict | None = None,
        severity: str = "info",
    ) -> AuditLog:
        """Create a new security audit log entry."""
        log_entry = await self.audit_repo.log(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            severity=severity,
        )
        return log_entry

    async def log_request(
        self,
        request: Request,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        user_id: UUID | None = None,
        details: dict | None = None,
        severity: str = "info",
    ) -> AuditLog:
        """Log user activity directly from a FastAPI Request object."""
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")

        return await self.log_activity(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            severity=severity,
        )

    async def get_logs(self, page: int = 1, page_size: int = 50, filters: dict | None = None) -> dict:
        """Get paginated and filtered list of audit logs (Admin only)."""
        skip = (page - 1) * page_size
        logs = await self.audit_repo.get_multi(
            skip=skip,
            limit=page_size,
            filters=filters,
            order_by="created_at",
            descending=True,
        )
        total = await self.audit_repo.count(filters=filters)
        return {
            "logs": [
                {
                    "id": str(log.id),
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "user_id": str(log.user_id) if log.user_id else None,
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent,
                    "details": log.details_json,
                    "severity": log.severity.value if hasattr(log.severity, "value") else log.severity,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                for log in logs
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_log_details(self, log_id: UUID) -> dict:
        """Retrieve full details of a specific audit log."""
        log = await self.audit_repo.get(log_id)
        if not log:
            raise NotFoundError("AuditLog", str(log_id))
        return {
            "id": str(log.id),
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "user_id": str(log.user_id) if log.user_id else None,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "details": log.details_json,
            "severity": log.severity.value if hasattr(log.severity, "value") else log.severity,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }

"""Small audit logging helper for security and traceability.

The helper is intentionally defensive: if the audit table has not been
migrated yet, it logs the failure but never blocks the business operation.
"""
from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger("academia360.audit")


def _safe_json(details: dict[str, Any] | None) -> str | None:
    if not details:
        return None
    return json.dumps(details, default=str, ensure_ascii=False)


def log_audit(
    cursor,
    *,
    current_user: dict | None = None,
    action: str,
    module: str,
    entity_type: str | None = None,
    entity_id: int | str | None = None,
    summary: str,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    """Insert an audit entry using the active transaction cursor.

    It swallows errors on purpose. Audit logging should never break the main
    operation, especially during a staged migration or on older demo databases.
    """
    try:
        cursor.execute(
            """
            INSERT INTO Tbl_AuditLogs (
                UserID,
                UserEmail,
                UserRole,
                Action,
                Module,
                EntityType,
                EntityID,
                Summary,
                Details,
                IpAddress,
                UserAgent
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                current_user.get("user_id") if current_user else None,
                current_user.get("email") if current_user else None,
                current_user.get("role") if current_user else None,
                action,
                module,
                entity_type,
                str(entity_id) if entity_id is not None else None,
                summary[:255],
                _safe_json(details),
                ip_address,
                user_agent[:255] if user_agent else None,
            ),
        )
    except Exception as exc:  # noqa: BLE001 - audit must be non-blocking
        logger.warning("Audit log skipped: %s", exc)

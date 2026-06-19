from datetime import date, datetime, time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from auth import require_roles
from db import get_db

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("")
def get_audit_logs(
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    module: Optional[str] = Query(default=None),
    action: Optional[str] = Query(default=None),
    user_id: Optional[int] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=300, ge=1, le=1000),
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director"])),
):
    cursor = connection.cursor(dictionary=True)
    clauses = []
    values = []

    if start_date is not None:
        clauses.append("CreatedAt >= %s")
        values.append(datetime.combine(start_date, time.min))
    if end_date is not None:
        clauses.append("CreatedAt <= %s")
        values.append(datetime.combine(end_date, time.max))
    if module:
        clauses.append("LOWER(Module) = %s")
        values.append(module.strip().lower())
    if action:
        clauses.append("LOWER(Action) = %s")
        values.append(action.strip().lower())
    if user_id is not None:
        clauses.append("UserID = %s")
        values.append(user_id)
    if search and search.strip():
        like = f"%{search.strip().lower()}%"
        clauses.append(
            """
            (
                LOWER(COALESCE(UserEmail, '')) LIKE %s
                OR LOWER(COALESCE(UserRole, '')) LIKE %s
                OR LOWER(COALESCE(Action, '')) LIKE %s
                OR LOWER(COALESCE(Module, '')) LIKE %s
                OR LOWER(COALESCE(EntityType, '')) LIKE %s
                OR LOWER(COALESCE(EntityID, '')) LIKE %s
                OR LOWER(COALESCE(Summary, '')) LIKE %s
            )
            """
        )
        values.extend([like] * 7)

    where_sql = ""
    if clauses:
        where_sql = "WHERE " + " AND ".join(clauses)

    try:
        cursor.execute(
            f"""
            SELECT
                AuditLogID AS id,
                UserID AS user_id,
                UserEmail AS user_email,
                UserRole AS user_role,
                Action AS action,
                Module AS module,
                EntityType AS entity_type,
                EntityID AS entity_id,
                Summary AS summary,
                Details AS details,
                IpAddress AS ip_address,
                UserAgent AS user_agent,
                CreatedAt AS created_at
            FROM Tbl_AuditLogs
            {where_sql}
            ORDER BY CreatedAt DESC, AuditLogID DESC
            LIMIT %s
            """,
            tuple([*values, limit]),
        )
        return cursor.fetchall()
    except Exception as exc:  # noqa: BLE001 - usually migration not applied
        raise HTTPException(
            status_code=500,
            detail=f"Audit log table is not ready. Run database/migration_audit_logs.sql. Original error: {exc}",
        )
    finally:
        cursor.close()


@router.get("/summary")
def get_audit_summary(
    days: int = Query(default=7, ge=1, le=90),
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director"])),
):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM Tbl_AuditLogs
            WHERE CreatedAt >= DATE_SUB(NOW(), INTERVAL %s DAY)
            """,
            (days,),
        )
        total = (cursor.fetchone() or {}).get("total", 0)

        cursor.execute(
            """
            SELECT Module AS module, COUNT(*) AS total
            FROM Tbl_AuditLogs
            WHERE CreatedAt >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY Module
            ORDER BY total DESC, Module
            LIMIT 8
            """,
            (days,),
        )
        by_module = cursor.fetchall()

        cursor.execute(
            """
            SELECT Action AS action, COUNT(*) AS total
            FROM Tbl_AuditLogs
            WHERE CreatedAt >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY Action
            ORDER BY total DESC, Action
            LIMIT 8
            """,
            (days,),
        )
        by_action = cursor.fetchall()

        return {"days": days, "total": total, "by_module": by_module, "by_action": by_action}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail=f"Audit log table is not ready. Run database/migration_audit_logs.sql. Original error: {exc}",
        )
    finally:
        cursor.close()

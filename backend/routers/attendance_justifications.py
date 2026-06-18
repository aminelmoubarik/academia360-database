from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_db
from models import AttendanceJustificationCreate, AttendanceJustificationUpdate
from utils import get_audit_username, model_to_dict

router = APIRouter(prefix="/attendance-justifications", tags=["Attendance Justifications"])


def _validate_dependencies(cursor, student_id, schedule_id=None):
    cursor.execute("SELECT StudentID FROM Tbl_Students WHERE StudentID = %s", (student_id,))
    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="Student not found")

    if schedule_id is not None:
        cursor.execute("SELECT ScheduleID FROM Tbl_GeneratedSchedule WHERE ScheduleID = %s", (schedule_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Schedule record not found")


@router.get("")
def get_justifications(
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                j.JustificationID AS id,
                j.StudentID AS student_id,
                s.FullName AS student_name,
                s.StudentNumber AS student_number,
                s.CardUID AS card_uid,
                cl.ClassID AS class_id,
                cl.Name AS class_name,
                j.ScheduleID AS schedule_id,
                d.Name AS discipline_name,
                sc.CalendarDate AS schedule_date,
                gs.StartTime AS schedule_start_time,
                gs.EndTime AS schedule_end_time,
                j.JustificationDate AS justification_date,
                j.Reason AS reason,
                j.Status AS status,
                j.DocumentPath AS document_path,
                j.ReviewedByUserID AS reviewed_by_user_id,
                ru.FullName AS reviewed_by_name,
                j.ReviewedAt AS reviewed_at,
                j.InsertUsername AS insert_username,
                j.InsertDate AS insert_date,
                j.ChangeUsername AS change_username,
                j.ChangeDate AS change_date
            FROM Tbl_AttendanceJustifications j
            JOIN Tbl_Students s ON j.StudentID = s.StudentID
            LEFT JOIN Tbl_Classes cl ON s.ClassID = cl.ClassID
            LEFT JOIN Tbl_GeneratedSchedule gs ON j.ScheduleID = gs.ScheduleID
            LEFT JOIN Tbl_SchoolCalendar sc ON gs.CalendarID = sc.CalendarID
            LEFT JOIN trx_Discipline_CourseYear dc ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
            LEFT JOIN Tbl_Disciplines d ON dc.DisciplineID = d.DisciplineID
            LEFT JOIN Tbl_Users ru ON j.ReviewedByUserID = ru.UserID
            ORDER BY j.JustificationDate DESC, j.JustificationID DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()


@router.get("/{justification_id}")
def get_justification(
    justification_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                j.JustificationID AS id,
                j.StudentID AS student_id,
                s.FullName AS student_name,
                j.ScheduleID AS schedule_id,
                j.JustificationDate AS justification_date,
                j.Reason AS reason,
                j.Status AS status,
                j.DocumentPath AS document_path,
                j.ReviewedByUserID AS reviewed_by_user_id,
                ru.FullName AS reviewed_by_name,
                j.ReviewedAt AS reviewed_at,
                j.InsertUsername AS insert_username,
                j.InsertDate AS insert_date,
                j.ChangeUsername AS change_username,
                j.ChangeDate AS change_date
            FROM Tbl_AttendanceJustifications j
            JOIN Tbl_Students s ON j.StudentID = s.StudentID
            LEFT JOIN Tbl_Users ru ON j.ReviewedByUserID = ru.UserID
            WHERE j.JustificationID = %s
        """, (justification_id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Attendance justification not found")
        return row
    finally:
        cursor.close()


@router.post("")
def create_justification(
    justification: AttendanceJustificationCreate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "secretary"]))
):
    cursor = connection.cursor(dictionary=True)
    audit_username = get_audit_username(current_user)
    try:
        _validate_dependencies(cursor, justification.student_id, justification.schedule_id)
        cursor.execute("""
            INSERT INTO Tbl_AttendanceJustifications (
                StudentID,
                ScheduleID,
                JustificationDate,
                Reason,
                Status,
                DocumentPath,
                InsertUsername
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            justification.student_id,
            justification.schedule_id,
            justification.justification_date,
            justification.reason,
            justification.status,
            justification.document_path,
            audit_username,
        ))
        connection.commit()
        return {"message": "Justification created successfully", "justification_id": cursor.lastrowid}
    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))
    finally:
        cursor.close()


@router.put("/{justification_id}")
def update_justification(
    justification_id: int,
    justification: AttendanceJustificationUpdate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    data = model_to_dict(justification)
    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    cursor = connection.cursor(dictionary=True)
    audit_username = get_audit_username(current_user)

    try:
        cursor.execute("SELECT * FROM Tbl_AttendanceJustifications WHERE JustificationID = %s", (justification_id,))
        existing = cursor.fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Attendance justification not found")

        student_id = data.get("student_id", existing["StudentID"])
        schedule_id = data.get("schedule_id", existing["ScheduleID"])
        _validate_dependencies(cursor, student_id, schedule_id)

        field_map = {
            "student_id": "StudentID",
            "schedule_id": "ScheduleID",
            "justification_date": "JustificationDate",
            "reason": "Reason",
            "status": "Status",
            "document_path": "DocumentPath",
        }

        set_clauses = []
        values = []
        for api_field, db_field in field_map.items():
            if api_field in data:
                set_clauses.append(f"{db_field} = %s")
                values.append(data[api_field])

        if "status" in data and data["status"] in ("approved", "rejected"):
            set_clauses.append("ReviewedByUserID = %s")
            values.append(current_user["user_id"])
            set_clauses.append("ReviewedAt = NOW()")
        elif "status" in data and data["status"] == "pending":
            set_clauses.append("ReviewedByUserID = NULL")
            set_clauses.append("ReviewedAt = NULL")

        set_clauses.append("ChangeUsername = %s")
        values.append(audit_username)
        values.append(justification_id)

        cursor.execute(f"""
            UPDATE Tbl_AttendanceJustifications
            SET {", ".join(set_clauses)}
            WHERE JustificationID = %s
        """, tuple(values))
        connection.commit()
        return {"message": "Justification updated successfully", "justification_id": justification_id}
    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))
    finally:
        cursor.close()


@router.delete("/{justification_id}")
def delete_justification(
    justification_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "secretary"]))
):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("DELETE FROM Tbl_AttendanceJustifications WHERE JustificationID = %s", (justification_id,))
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Attendance justification not found")
        return {"message": "Justification deleted successfully", "justification_id": justification_id}
    except IntegrityError:
        connection.rollback()
        raise HTTPException(status_code=400, detail="Justification cannot be deleted because it is being used by another record")
    finally:
        cursor.close()

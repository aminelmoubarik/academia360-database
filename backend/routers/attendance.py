from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_db
from models import (
    AttendanceCreate,
    AttendancePunchRequest,
    AttendanceUpdate,
    OfflineAttendanceSyncRequest,
)
from utils import get_audit_username, model_to_dict

router = APIRouter(prefix="/attendance", tags=["Attendance"])


def validate_student_exists(cursor, student_id: int):
    cursor.execute("""
        SELECT StudentID
        FROM Tbl_Students
        WHERE StudentID = %s
    """, (student_id,))

    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="Student not found")


def validate_schedule_exists(cursor, schedule_id: int | None):
    if schedule_id is None:
        return

    cursor.execute("""
        SELECT ScheduleID
        FROM Tbl_GeneratedSchedule
        WHERE ScheduleID = %s
    """, (schedule_id,))

    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="Schedule record not found")


def get_student_by_card(cursor, card_uid: str):
    cleaned = card_uid.strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="Card UID is required")

    cursor.execute("""
        SELECT
            s.StudentID AS student_id,
            s.FullName AS student_name,
            s.StudentNumber AS student_number,
            s.CardUID AS card_uid,
            s.ClassID AS class_id,
            cl.Name AS class_name,
            c.Code AS course_code
        FROM Tbl_Students s
        LEFT JOIN Tbl_Classes cl ON s.ClassID = cl.ClassID
        LEFT JOIN Tbl_Courses c ON cl.CourseID = c.CourseID
        WHERE s.CardUID = %s OR s.StudentNumber = %s
        LIMIT 1
    """, (cleaned, cleaned))

    student = cursor.fetchone()
    if student is None:
        raise HTTPException(
            status_code=404,
            detail="No student found for this card/identifier"
        )
    return student


def resolve_auto_punch_type(cursor, student_id: int, punch_time: datetime | None):
    target = punch_time or datetime.now()
    cursor.execute("""
        SELECT PunchType
        FROM Tbl_AttendanceRecords
        WHERE StudentID = %s
          AND DATE(PunchTime) = %s
        ORDER BY PunchTime DESC, AttendanceRecordID DESC
        LIMIT 1
    """, (student_id, target.date()))

    last = cursor.fetchone()
    if last is not None and last["PunchType"] == "in":
        return "out"
    return "in"


def find_current_schedule(cursor, class_id: int | None, punch_time: datetime | None):
    if class_id is None:
        return None

    target = punch_time or datetime.now()
    target_date = target.date()
    target_time = target.time()

    cursor.execute("""
        SELECT gs.ScheduleID AS schedule_id
        FROM Tbl_GeneratedSchedule gs
        JOIN Tbl_SchoolCalendar sc ON gs.CalendarID = sc.CalendarID
        WHERE gs.ClassID = %s
          AND sc.CalendarDate = %s
          AND gs.StartTime <= %s
          AND gs.EndTime >= %s
          AND gs.Status <> 'cancelled'
        ORDER BY gs.StartTime
        LIMIT 1
    """, (class_id, target_date, target_time, target_time))

    schedule = cursor.fetchone()
    return None if schedule is None else schedule["schedule_id"]


def insert_attendance_record(
    cursor,
    *,
    student_id: int,
    schedule_id: int | None,
    punch_type: str,
    punch_method: str,
    punch_time: datetime | None,
    is_synced: bool,
    audit_username: str,
):
    cursor.execute("""
        INSERT INTO Tbl_AttendanceRecords (
            StudentID,
            ScheduleID,
            PunchType,
            PunchMethod,
            PunchTime,
            IsSynced,
            InsertUsername
        )
        VALUES (%s, %s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP), %s, %s)
    """, (
        student_id,
        schedule_id,
        punch_type,
        punch_method,
        punch_time,
        is_synced,
        audit_username,
    ))
    return cursor.lastrowid


def build_punch_response(cursor, attendance_record_id: int, student: dict, punch_type: str, schedule_id: int | None):
    cursor.execute("""
        SELECT PunchTime AS punch_time
        FROM Tbl_AttendanceRecords
        WHERE AttendanceRecordID = %s
    """, (attendance_record_id,))
    punch = cursor.fetchone() or {}
    return {
        "success": True,
        "message": "Attendance punch registered successfully",
        "attendance_record_id": attendance_record_id,
        "student": student,
        "punch_type": punch_type,
        "schedule_id": schedule_id,
        "punch_time": punch.get("punch_time"),
    }


@router.get("")
def get_attendance_records(
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                ar.AttendanceRecordID AS id,
                ar.StudentID AS student_id,
                s.FullName AS student_name,
                s.StudentNumber AS student_number,
                s.CardUID AS card_uid,
                cl.ClassID AS class_id,
                cl.Name AS class_name,
                c.Code AS course_code,
                sy.Name AS school_year,
                ar.ScheduleID AS schedule_id,
                d.Name AS discipline_name,
                sc.CalendarDate AS schedule_date,
                gs.StartTime AS class_start_time,
                gs.EndTime AS class_end_time,
                ar.PunchType AS punch_type,
                ar.PunchMethod AS punch_method,
                ar.PunchTime AS punch_time,
                ar.IsSynced AS is_synced,
                ar.InsertUsername AS insert_username,
                ar.InsertDate AS insert_date,
                ar.ChangeUsername AS change_username,
                ar.ChangeDate AS change_date
            FROM Tbl_AttendanceRecords ar
            JOIN Tbl_Students s 
                ON ar.StudentID = s.StudentID
            LEFT JOIN Tbl_Classes cl 
                ON s.ClassID = cl.ClassID
            LEFT JOIN Tbl_Courses c 
                ON cl.CourseID = c.CourseID
            LEFT JOIN Tref_SchoolYears sy 
                ON cl.SchoolYearID = sy.SchoolYearID
            LEFT JOIN Tbl_GeneratedSchedule gs 
                ON ar.ScheduleID = gs.ScheduleID
            LEFT JOIN Tbl_SchoolCalendar sc 
                ON gs.CalendarID = sc.CalendarID
            LEFT JOIN trx_Discipline_CourseYear dc 
                ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
            LEFT JOIN Tbl_Disciplines d 
                ON dc.DisciplineID = d.DisciplineID
            ORDER BY ar.PunchTime DESC
        """)

        return cursor.fetchall()

    finally:
        cursor.close()


@router.get("/dashboard")
def get_attendance_dashboard(
    target_date: date | None = None,
    class_id: int | None = None,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    target_date = target_date or date.today()
    cursor = connection.cursor(dictionary=True)

    try:
        class_clause = ""
        class_values = []
        if class_id is not None:
            class_clause = "AND s.ClassID = %s"
            class_values.append(class_id)

        cursor.execute(f"""
            SELECT COUNT(*) AS total_students
            FROM Tbl_Students s
            WHERE 1 = 1 {class_clause}
        """, tuple(class_values))
        total_students = (cursor.fetchone() or {}).get("total_students", 0)

        cursor.execute(f"""
            SELECT COUNT(DISTINCT ar.StudentID) AS present_students
            FROM Tbl_AttendanceRecords ar
            JOIN Tbl_Students s ON ar.StudentID = s.StudentID
            WHERE DATE(ar.PunchTime) = %s
              AND ar.PunchType = 'in'
              {class_clause}
        """, (target_date, *class_values))
        present_students = (cursor.fetchone() or {}).get("present_students", 0)

        cursor.execute(f"""
            SELECT
                s.StudentID AS student_id,
                s.FullName AS student_name,
                s.StudentNumber AS student_number,
                s.CardUID AS card_uid,
                cl.Name AS class_name
            FROM Tbl_Students s
            LEFT JOIN Tbl_Classes cl ON s.ClassID = cl.ClassID
            LEFT JOIN Tbl_AttendanceRecords ar
              ON ar.StudentID = s.StudentID
             AND DATE(ar.PunchTime) = %s
             AND ar.PunchType = 'in'
            WHERE ar.AttendanceRecordID IS NULL
              {class_clause}
            ORDER BY cl.Name, s.FullName
            LIMIT 20
        """, (target_date, *class_values))
        absentees = cursor.fetchall()

        cursor.execute(f"""
            SELECT
                ar.AttendanceRecordID AS id,
                s.FullName AS student_name,
                s.StudentNumber AS student_number,
                cl.Name AS class_name,
                ar.PunchType AS punch_type,
                ar.PunchMethod AS punch_method,
                ar.PunchTime AS punch_time
            FROM Tbl_AttendanceRecords ar
            JOIN Tbl_Students s ON ar.StudentID = s.StudentID
            LEFT JOIN Tbl_Classes cl ON s.ClassID = cl.ClassID
            WHERE DATE(ar.PunchTime) = %s
              {class_clause}
            ORDER BY ar.PunchTime DESC
            LIMIT 12
        """, (target_date, *class_values))
        recent = cursor.fetchall()

        return {
            "date": target_date,
            "total_students": total_students,
            "present_students": present_students,
            "absent_students": max(total_students - present_students, 0),
            "absentees": absentees,
            "recent": recent,
            "alerts": [
                {
                    "type": "absenteeism",
                    "message": f"{max(total_students - present_students, 0)} estudantes sem picagem de entrada hoje",
                }
            ] if total_students - present_students > 0 else [],
        }

    finally:
        cursor.close()


@router.post("/punch")
def punch_attendance(
    request: AttendancePunchRequest,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)
    audit_username = get_audit_username(current_user)

    try:
        student = get_student_by_card(cursor, request.card_uid)
        punch_type = request.punch_type or resolve_auto_punch_type(
            cursor=cursor,
            student_id=student["student_id"],
            punch_time=request.punch_time,
        )
        schedule_id = find_current_schedule(
            cursor=cursor,
            class_id=student.get("class_id"),
            punch_time=request.punch_time,
        )
        attendance_id = insert_attendance_record(
            cursor,
            student_id=student["student_id"],
            schedule_id=schedule_id,
            punch_type=punch_type,
            punch_method=request.punch_method,
            punch_time=request.punch_time,
            is_synced=request.is_synced,
            audit_username=audit_username,
        )
        connection.commit()
        return build_punch_response(cursor, attendance_id, student, punch_type, schedule_id)

    except HTTPException:
        connection.rollback()
        raise
    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))
    finally:
        cursor.close()


@router.post("/offline-sync")
def sync_offline_attendance(
    request: OfflineAttendanceSyncRequest,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)
    audit_username = get_audit_username(current_user)
    synced = []
    failed = []

    try:
        for index, item in enumerate(request.records):
            try:
                student = get_student_by_card(cursor, item.card_uid)
                punch_type = item.punch_type or resolve_auto_punch_type(
                    cursor,
                    student["student_id"],
                    item.punch_time,
                )
                schedule_id = find_current_schedule(cursor, student.get("class_id"), item.punch_time)
                attendance_id = insert_attendance_record(
                    cursor,
                    student_id=student["student_id"],
                    schedule_id=schedule_id,
                    punch_type=punch_type,
                    punch_method=item.punch_method,
                    punch_time=item.punch_time,
                    is_synced=True,
                    audit_username=audit_username,
                )
                synced.append({"index": index, "attendance_record_id": attendance_id})
            except Exception as exc:  # noqa: BLE001 - queremos devolver os erros por registo
                failed.append({"index": index, "card_uid": item.card_uid, "error": str(exc)})

        if failed:
            connection.rollback()
            return {"success": False, "synced": synced, "failed": failed}

        connection.commit()
        return {"success": True, "synced": synced, "failed": []}

    finally:
        cursor.close()


@router.get("/student/{student_id}")
def get_attendance_by_student(
    student_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        validate_student_exists(cursor, student_id)

        cursor.execute("""
            SELECT
                ar.AttendanceRecordID AS id,
                ar.StudentID AS student_id,
                s.FullName AS student_name,
                s.StudentNumber AS student_number,
                ar.ScheduleID AS schedule_id,
                d.Name AS discipline_name,
                sc.CalendarDate AS schedule_date,
                gs.StartTime AS class_start_time,
                gs.EndTime AS class_end_time,
                ar.PunchType AS punch_type,
                ar.PunchMethod AS punch_method,
                ar.PunchTime AS punch_time,
                ar.IsSynced AS is_synced
            FROM Tbl_AttendanceRecords ar
            JOIN Tbl_Students s 
                ON ar.StudentID = s.StudentID
            LEFT JOIN Tbl_GeneratedSchedule gs 
                ON ar.ScheduleID = gs.ScheduleID
            LEFT JOIN Tbl_SchoolCalendar sc 
                ON gs.CalendarID = sc.CalendarID
            LEFT JOIN trx_Discipline_CourseYear dc 
                ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
            LEFT JOIN Tbl_Disciplines d 
                ON dc.DisciplineID = d.DisciplineID
            WHERE ar.StudentID = %s
            ORDER BY ar.PunchTime DESC
        """, (student_id,))

        return cursor.fetchall()

    finally:
        cursor.close()


@router.get("/schedule/{schedule_id}")
def get_attendance_by_schedule(
    schedule_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        validate_schedule_exists(cursor, schedule_id)

        cursor.execute("""
            SELECT
                ar.AttendanceRecordID AS id,
                ar.StudentID AS student_id,
                s.FullName AS student_name,
                s.StudentNumber AS student_number,
                ar.ScheduleID AS schedule_id,
                d.Name AS discipline_name,
                sc.CalendarDate AS schedule_date,
                gs.StartTime AS class_start_time,
                gs.EndTime AS class_end_time,
                ar.PunchType AS punch_type,
                ar.PunchMethod AS punch_method,
                ar.PunchTime AS punch_time,
                ar.IsSynced AS is_synced
            FROM Tbl_AttendanceRecords ar
            JOIN Tbl_Students s 
                ON ar.StudentID = s.StudentID
            LEFT JOIN Tbl_GeneratedSchedule gs 
                ON ar.ScheduleID = gs.ScheduleID
            LEFT JOIN Tbl_SchoolCalendar sc 
                ON gs.CalendarID = sc.CalendarID
            LEFT JOIN trx_Discipline_CourseYear dc 
                ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
            LEFT JOIN Tbl_Disciplines d 
                ON dc.DisciplineID = d.DisciplineID
            WHERE ar.ScheduleID = %s
            ORDER BY ar.PunchTime DESC
        """, (schedule_id,))

        return cursor.fetchall()

    finally:
        cursor.close()


@router.get("/{attendance_id}")
def get_attendance_record(
    attendance_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                ar.AttendanceRecordID AS id,
                ar.StudentID AS student_id,
                s.FullName AS student_name,
                s.StudentNumber AS student_number,
                s.CardUID AS card_uid,
                cl.ClassID AS class_id,
                cl.Name AS class_name,
                c.Code AS course_code,
                sy.Name AS school_year,
                ar.ScheduleID AS schedule_id,
                d.Name AS discipline_name,
                sc.CalendarDate AS schedule_date,
                gs.StartTime AS class_start_time,
                gs.EndTime AS class_end_time,
                ar.PunchType AS punch_type,
                ar.PunchMethod AS punch_method,
                ar.PunchTime AS punch_time,
                ar.IsSynced AS is_synced,
                ar.InsertUsername AS insert_username,
                ar.InsertDate AS insert_date,
                ar.ChangeUsername AS change_username,
                ar.ChangeDate AS change_date
            FROM Tbl_AttendanceRecords ar
            JOIN Tbl_Students s 
                ON ar.StudentID = s.StudentID
            LEFT JOIN Tbl_Classes cl 
                ON s.ClassID = cl.ClassID
            LEFT JOIN Tbl_Courses c 
                ON cl.CourseID = c.CourseID
            LEFT JOIN Tref_SchoolYears sy 
                ON cl.SchoolYearID = sy.SchoolYearID
            LEFT JOIN Tbl_GeneratedSchedule gs 
                ON ar.ScheduleID = gs.ScheduleID
            LEFT JOIN Tbl_SchoolCalendar sc 
                ON gs.CalendarID = sc.CalendarID
            LEFT JOIN trx_Discipline_CourseYear dc 
                ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
            LEFT JOIN Tbl_Disciplines d 
                ON dc.DisciplineID = d.DisciplineID
            WHERE ar.AttendanceRecordID = %s
        """, (attendance_id,))

        record = cursor.fetchone()

        if record is None:
            raise HTTPException(
                status_code=404,
                detail="Attendance record not found"
            )

        return record

    finally:
        cursor.close()


@router.post("")
def create_attendance_record(
    attendance: AttendanceCreate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)
    audit_username = get_audit_username(current_user)

    try:
        validate_student_exists(cursor, attendance.student_id)
        validate_schedule_exists(cursor, attendance.schedule_id)

        attendance_id = insert_attendance_record(
            cursor,
            student_id=attendance.student_id,
            schedule_id=attendance.schedule_id,
            punch_type=attendance.punch_type,
            punch_method=attendance.punch_method,
            punch_time=attendance.punch_time,
            is_synced=attendance.is_synced,
            audit_username=audit_username,
        )

        connection.commit()

        return {
            "message": "Attendance record created successfully",
            "attendance_record_id": attendance_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.put("/{attendance_id}")
def update_attendance_record(
    attendance_id: int,
    attendance: AttendanceUpdate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "secretary"]))
):
    data = model_to_dict(attendance)

    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    cursor = connection.cursor(dictionary=True)
    audit_username = get_audit_username(current_user)

    try:
        cursor.execute("""
            SELECT AttendanceRecordID
            FROM Tbl_AttendanceRecords
            WHERE AttendanceRecordID = %s
        """, (attendance_id,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Attendance record not found"
            )

        if "student_id" in data:
            validate_student_exists(cursor, data["student_id"])

        if "schedule_id" in data:
            validate_schedule_exists(cursor, data["schedule_id"])

        field_map = {
            "student_id": "StudentID",
            "schedule_id": "ScheduleID",
            "punch_type": "PunchType",
            "punch_method": "PunchMethod",
            "is_synced": "IsSynced"
        }

        set_clauses = []
        values = []

        for api_field, db_field in field_map.items():
            if api_field in data:
                set_clauses.append(f"{db_field} = %s")
                values.append(data[api_field])

        if not set_clauses:
            raise HTTPException(status_code=400, detail="No valid fields provided for update")

        set_clauses.append("ChangeUsername = %s")
        values.append(audit_username)

        values.append(attendance_id)

        cursor.execute(f"""
            UPDATE Tbl_AttendanceRecords
            SET {", ".join(set_clauses)}
            WHERE AttendanceRecordID = %s
        """, tuple(values))

        connection.commit()
  
        return {
            "message": "Attendance record updated successfully",
            "attendance_record_id": attendance_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.delete("/{attendance_id}")
def delete_attendance_record(
    attendance_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "secretary"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            DELETE FROM Tbl_AttendanceRecords
            WHERE AttendanceRecordID = %s
        """, (attendance_id,))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Attendance record not found"
            )

        return {
            "message": "Attendance record deleted successfully",
            "attendance_record_id": attendance_id
        }

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="Attendance record cannot be deleted because it is being used by another record"
        )

    finally:
        cursor.close()

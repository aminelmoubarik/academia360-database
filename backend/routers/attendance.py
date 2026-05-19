from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_connection
from models import AttendanceCreate, AttendanceUpdate
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


@router.get("")
def get_attendance_records(
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
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
        connection.close()


@router.get("/student/{student_id}")
def get_attendance_by_student(
    student_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
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
        connection.close()


@router.get("/schedule/{schedule_id}")
def get_attendance_by_schedule(
    schedule_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
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
        connection.close()


@router.get("/{attendance_id}")
def get_attendance_record(
    attendance_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
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
        connection.close()


@router.post("")
def create_attendance_record(
    attendance: AttendanceCreate,
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        validate_student_exists(cursor, attendance.student_id)
        validate_schedule_exists(cursor, attendance.schedule_id)

        cursor.execute("""
            INSERT INTO Tbl_AttendanceRecords (
                StudentID,
                ScheduleID,
                PunchType,
                PunchMethod,
                IsSynced,
                InsertUsername
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            attendance.student_id,
            attendance.schedule_id,
            attendance.punch_type,
            attendance.punch_method,
            attendance.is_synced,
            audit_username
        ))

        connection.commit()

        return {
            "message": "Attendance record created successfully",
            "attendance_record_id": cursor.lastrowid
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()
        connection.close()


@router.put("/{attendance_id}")
def update_attendance_record(
    attendance_id: int,
    attendance: AttendanceUpdate,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    data = model_to_dict(attendance)

    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    connection = get_connection()
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
        connection.close()


@router.delete("/{attendance_id}")
def delete_attendance_record(
    attendance_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    connection = get_connection()
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
        connection.close()
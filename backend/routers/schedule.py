from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_connection
from models import ScheduleCreate, ScheduleUpdate
from utils import get_audit_username, model_to_dict

router = APIRouter(prefix="/schedule", tags=["Schedule"])


def validate_time_range(start_time, end_time):
    if start_time is not None and end_time is not None:
        if end_time <= start_time:
            raise HTTPException(
                status_code=400,
                detail="End time must be greater than start time"
            )


def get_existing_schedule(cursor, schedule_id: int):
    cursor.execute("""
        SELECT
            ScheduleID,
            ClassID,
            DisciplineCourseYearID,
            ProfessorID,
            RoomID,
            CalendarID,
            StartTime,
            EndTime,
            Status
        FROM Tbl_GeneratedSchedule
        WHERE ScheduleID = %s
    """, (schedule_id,))

    schedule = cursor.fetchone()

    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule record not found")

    return schedule


def validate_schedule_dependencies(
    cursor,
    class_id,
    discipline_course_year_id,
    professor_id,
    room_id,
    calendar_id
):
    cursor.execute("""
        SELECT
            ClassID,
            CourseID,
            SchoolYearID,
            CourseYearNumber
        FROM Tbl_Classes
        WHERE ClassID = %s
    """, (class_id,))
    class_record = cursor.fetchone()

    if class_record is None:
        raise HTTPException(status_code=404, detail="Class not found")

    cursor.execute("""
        SELECT
            DisciplineCourseYearID,
            CourseID,
            SchoolYearID,
            CourseYearNumber,
            IsPractical
        FROM trx_Discipline_CourseYear
        WHERE DisciplineCourseYearID = %s
    """, (discipline_course_year_id,))
    discipline_course_year = cursor.fetchone()

    if discipline_course_year is None:
        raise HTTPException(
            status_code=404,
            detail="Discipline course year record not found"
        )

    cursor.execute("""
        SELECT ProfessorID
        FROM Tbl_Professors
        WHERE ProfessorID = %s
    """, (professor_id,))
    professor = cursor.fetchone()

    if professor is None:
        raise HTTPException(status_code=404, detail="Professor not found")

    cursor.execute("""
        SELECT
            RoomID,
            IsPracticeRoom
        FROM Tbl_Rooms
        WHERE RoomID = %s
    """, (room_id,))
    room = cursor.fetchone()

    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    cursor.execute("""
        SELECT
            CalendarID,
            SchoolYearID,
            CalendarDate,
            IsSchoolDay
        FROM Tbl_SchoolCalendar
        WHERE CalendarID = %s
    """, (calendar_id,))
    calendar = cursor.fetchone()

    if calendar is None:
        raise HTTPException(status_code=404, detail="Calendar record not found")

    if not calendar["IsSchoolDay"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot create schedule on a non-school day"
        )

    if class_record["CourseID"] != discipline_course_year["CourseID"]:
        raise HTTPException(
            status_code=400,
            detail="Class course does not match discipline course"
        )

    if class_record["SchoolYearID"] != discipline_course_year["SchoolYearID"]:
        raise HTTPException(
            status_code=400,
            detail="Class school year does not match discipline school year"
        )

    if class_record["CourseYearNumber"] != discipline_course_year["CourseYearNumber"]:
        raise HTTPException(
            status_code=400,
            detail="Class course year number does not match discipline course year number"
        )

    if calendar["SchoolYearID"] != class_record["SchoolYearID"]:
        raise HTTPException(
            status_code=400,
            detail="Calendar school year does not match class school year"
        )

    cursor.execute("""
        SELECT 1
        FROM trx_Professor_DisciplineCourseYear
        WHERE ProfessorID = %s
          AND DisciplineCourseYearID = %s
    """, (
        professor_id,
        discipline_course_year_id
    ))
    professor_assignment = cursor.fetchone()

    if professor_assignment is None:
        raise HTTPException(
            status_code=400,
            detail="Professor is not assigned to this discipline course year"
        )

    if discipline_course_year["IsPractical"] and not room["IsPracticeRoom"]:
        raise HTTPException(
            status_code=400,
            detail="Practical disciplines must be scheduled in a practice room"
        )


def validate_schedule_conflicts(
    cursor,
    class_id,
    professor_id,
    room_id,
    calendar_id,
    start_time,
    end_time,
    excluded_schedule_id=None
):
    excluded_clause = ""
    excluded_values = []

    if excluded_schedule_id is not None:
        excluded_clause = "AND ScheduleID <> %s"
        excluded_values = [excluded_schedule_id]

    cursor.execute(f"""
        SELECT ScheduleID
        FROM Tbl_GeneratedSchedule
        WHERE ClassID = %s
          AND CalendarID = %s
          AND NOT (EndTime <= %s OR StartTime >= %s)
          {excluded_clause}
        LIMIT 1
    """, (
        class_id,
        calendar_id,
        start_time,
        end_time,
        *excluded_values
    ))

    if cursor.fetchone() is not None:
        raise HTTPException(
            status_code=409,
            detail="Schedule conflict: this class already has another lesson at this time"
        )

    cursor.execute(f"""
        SELECT ScheduleID
        FROM Tbl_GeneratedSchedule
        WHERE ProfessorID = %s
          AND CalendarID = %s
          AND NOT (EndTime <= %s OR StartTime >= %s)
          {excluded_clause}
        LIMIT 1
    """, (
        professor_id,
        calendar_id,
        start_time,
        end_time,
        *excluded_values
    ))

    if cursor.fetchone() is not None:
        raise HTTPException(
            status_code=409,
            detail="Schedule conflict: this professor already has another lesson at this time"
        )

    cursor.execute(f"""
        SELECT ScheduleID
        FROM Tbl_GeneratedSchedule
        WHERE RoomID = %s
          AND CalendarID = %s
          AND NOT (EndTime <= %s OR StartTime >= %s)
          {excluded_clause}
        LIMIT 1
    """, (
        room_id,
        calendar_id,
        start_time,
        end_time,
        *excluded_values
    ))

    if cursor.fetchone() is not None:
        raise HTTPException(
            status_code=409,
            detail="Schedule conflict: this room is already being used at this time"
        )


@router.get("")
def get_schedule(
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                gs.ScheduleID AS id,
                gs.ClassID AS class_id,
                cl.Name AS class_name,
                c.CourseID AS course_id,
                c.Code AS course_code,
                c.Name AS course_name,
                sy.SchoolYearID AS school_year_id,
                sy.Name AS school_year,
                gs.DisciplineCourseYearID AS discipline_course_year_id,
                d.DisciplineID AS discipline_id,
                d.Name AS discipline_name,
                d.Code AS discipline_code,
                gs.ProfessorID AS professor_id,
                u.FullName AS professor_name,
                u.Email AS professor_email,
                gs.RoomID AS room_id,
                r.Name AS room_name,
                gs.CalendarID AS calendar_id,
                sc.CalendarDate AS schedule_date,
                gs.StartTime AS start_time,
                gs.EndTime AS end_time,
                gs.Status AS status,
                gs.InsertUsername AS insert_username,
                gs.InsertDate AS insert_date,
                gs.ChangeUsername AS change_username,
                gs.ChangeDate AS change_date
            FROM Tbl_GeneratedSchedule gs
            JOIN Tbl_Classes cl ON gs.ClassID = cl.ClassID
            JOIN Tbl_Courses c ON cl.CourseID = c.CourseID
            JOIN Tref_SchoolYears sy ON cl.SchoolYearID = sy.SchoolYearID
            JOIN trx_Discipline_CourseYear dc 
                ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
            JOIN Tbl_Disciplines d 
                ON dc.DisciplineID = d.DisciplineID
            JOIN Tbl_Professors p 
                ON gs.ProfessorID = p.ProfessorID
            JOIN Tbl_Users u 
                ON p.UserID = u.UserID
            JOIN Tbl_Rooms r 
                ON gs.RoomID = r.RoomID
            JOIN Tbl_SchoolCalendar sc 
                ON gs.CalendarID = sc.CalendarID
            ORDER BY sc.CalendarDate, gs.StartTime
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


@router.get("/class/{class_id}")
def get_schedule_by_class(
    class_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                gs.ScheduleID AS id,
                gs.ClassID AS class_id,
                cl.Name AS class_name,
                d.Name AS discipline_name,
                u.FullName AS professor_name,
                r.Name AS room_name,
                sc.CalendarDate AS schedule_date,
                gs.StartTime AS start_time,
                gs.EndTime AS end_time,
                gs.Status AS status
            FROM Tbl_GeneratedSchedule gs
            JOIN Tbl_Classes cl ON gs.ClassID = cl.ClassID
            JOIN trx_Discipline_CourseYear dc 
                ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
            JOIN Tbl_Disciplines d 
                ON dc.DisciplineID = d.DisciplineID
            JOIN Tbl_Professors p 
                ON gs.ProfessorID = p.ProfessorID
            JOIN Tbl_Users u 
                ON p.UserID = u.UserID
            JOIN Tbl_Rooms r 
                ON gs.RoomID = r.RoomID
            JOIN Tbl_SchoolCalendar sc 
                ON gs.CalendarID = sc.CalendarID
            WHERE gs.ClassID = %s
            ORDER BY sc.CalendarDate, gs.StartTime
        """, (class_id,))

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


@router.get("/professor/{professor_id}")
def get_schedule_by_professor(
    professor_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                gs.ScheduleID AS id,
                gs.ProfessorID AS professor_id,
                u.FullName AS professor_name,
                cl.Name AS class_name,
                d.Name AS discipline_name,
                r.Name AS room_name,
                sc.CalendarDate AS schedule_date,
                gs.StartTime AS start_time,
                gs.EndTime AS end_time,
                gs.Status AS status
            FROM Tbl_GeneratedSchedule gs
            JOIN Tbl_Classes cl ON gs.ClassID = cl.ClassID
            JOIN trx_Discipline_CourseYear dc 
                ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
            JOIN Tbl_Disciplines d 
                ON dc.DisciplineID = d.DisciplineID
            JOIN Tbl_Professors p 
                ON gs.ProfessorID = p.ProfessorID
            JOIN Tbl_Users u 
                ON p.UserID = u.UserID
            JOIN Tbl_Rooms r 
                ON gs.RoomID = r.RoomID
            JOIN Tbl_SchoolCalendar sc 
                ON gs.CalendarID = sc.CalendarID
            WHERE gs.ProfessorID = %s
            ORDER BY sc.CalendarDate, gs.StartTime
        """, (professor_id,))

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


@router.get("/room/{room_id}")
def get_schedule_by_room(
    room_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                gs.ScheduleID AS id,
                gs.RoomID AS room_id,
                r.Name AS room_name,
                cl.Name AS class_name,
                d.Name AS discipline_name,
                u.FullName AS professor_name,
                sc.CalendarDate AS schedule_date,
                gs.StartTime AS start_time,
                gs.EndTime AS end_time,
                gs.Status AS status
            FROM Tbl_GeneratedSchedule gs
            JOIN Tbl_Classes cl ON gs.ClassID = cl.ClassID
            JOIN trx_Discipline_CourseYear dc 
                ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
            JOIN Tbl_Disciplines d 
                ON dc.DisciplineID = d.DisciplineID
            JOIN Tbl_Professors p 
                ON gs.ProfessorID = p.ProfessorID
            JOIN Tbl_Users u 
                ON p.UserID = u.UserID
            JOIN Tbl_Rooms r 
                ON gs.RoomID = r.RoomID
            JOIN Tbl_SchoolCalendar sc 
                ON gs.CalendarID = sc.CalendarID
            WHERE gs.RoomID = %s
            ORDER BY sc.CalendarDate, gs.StartTime
        """, (room_id,))

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


@router.get("/{schedule_id}")
def get_schedule_record(
    schedule_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                gs.ScheduleID AS id,
                gs.ClassID AS class_id,
                cl.Name AS class_name,
                c.CourseID AS course_id,
                c.Code AS course_code,
                c.Name AS course_name,
                sy.SchoolYearID AS school_year_id,
                sy.Name AS school_year,
                gs.DisciplineCourseYearID AS discipline_course_year_id,
                d.DisciplineID AS discipline_id,
                d.Name AS discipline_name,
                d.Code AS discipline_code,
                gs.ProfessorID AS professor_id,
                u.FullName AS professor_name,
                u.Email AS professor_email,
                gs.RoomID AS room_id,
                r.Name AS room_name,
                gs.CalendarID AS calendar_id,
                sc.CalendarDate AS schedule_date,
                gs.StartTime AS start_time,
                gs.EndTime AS end_time,
                gs.Status AS status,
                gs.InsertUsername AS insert_username,
                gs.InsertDate AS insert_date,
                gs.ChangeUsername AS change_username,
                gs.ChangeDate AS change_date
            FROM Tbl_GeneratedSchedule gs
            JOIN Tbl_Classes cl ON gs.ClassID = cl.ClassID
            JOIN Tbl_Courses c ON cl.CourseID = c.CourseID
            JOIN Tref_SchoolYears sy ON cl.SchoolYearID = sy.SchoolYearID
            JOIN trx_Discipline_CourseYear dc 
                ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
            JOIN Tbl_Disciplines d 
                ON dc.DisciplineID = d.DisciplineID
            JOIN Tbl_Professors p 
                ON gs.ProfessorID = p.ProfessorID
            JOIN Tbl_Users u 
                ON p.UserID = u.UserID
            JOIN Tbl_Rooms r 
                ON gs.RoomID = r.RoomID
            JOIN Tbl_SchoolCalendar sc 
                ON gs.CalendarID = sc.CalendarID
            WHERE gs.ScheduleID = %s
        """, (schedule_id,))

        schedule = cursor.fetchone()

        if schedule is None:
            raise HTTPException(status_code=404, detail="Schedule record not found")

        return schedule

    finally:
        cursor.close()
        connection.close()


@router.post("")
def create_schedule_record(
    schedule: ScheduleCreate,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    validate_time_range(schedule.start_time, schedule.end_time)

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        validate_schedule_dependencies(
            cursor=cursor,
            class_id=schedule.class_id,
            discipline_course_year_id=schedule.discipline_course_year_id,
            professor_id=schedule.professor_id,
            room_id=schedule.room_id,
            calendar_id=schedule.calendar_id
        )

        validate_schedule_conflicts(
            cursor=cursor,
            class_id=schedule.class_id,
            professor_id=schedule.professor_id,
            room_id=schedule.room_id,
            calendar_id=schedule.calendar_id,
            start_time=schedule.start_time,
            end_time=schedule.end_time
        )

        cursor.execute("""
            INSERT INTO Tbl_GeneratedSchedule (
                ClassID,
                DisciplineCourseYearID,
                ProfessorID,
                RoomID,
                CalendarID,
                StartTime,
                EndTime,
                Status,
                InsertUsername
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            schedule.class_id,
            schedule.discipline_course_year_id,
            schedule.professor_id,
            schedule.room_id,
            schedule.calendar_id,
            schedule.start_time,
            schedule.end_time,
            schedule.status,
            audit_username
        ))

        connection.commit()

        return {
            "message": "Schedule record created successfully",
            "schedule_id": cursor.lastrowid
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()
        connection.close()


@router.put("/{schedule_id}")
def update_schedule_record(
    schedule_id: int,
    schedule: ScheduleUpdate,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    data = model_to_dict(schedule)

    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        existing_schedule = get_existing_schedule(cursor, schedule_id)

        merged_schedule = {
            "class_id": data.get("class_id", existing_schedule["ClassID"]),
            "discipline_course_year_id": data.get(
                "discipline_course_year_id",
                existing_schedule["DisciplineCourseYearID"]
            ),
            "professor_id": data.get("professor_id", existing_schedule["ProfessorID"]),
            "room_id": data.get("room_id", existing_schedule["RoomID"]),
            "calendar_id": data.get("calendar_id", existing_schedule["CalendarID"]),
            "start_time": data.get("start_time", existing_schedule["StartTime"]),
            "end_time": data.get("end_time", existing_schedule["EndTime"])
        }

        validate_time_range(
            merged_schedule["start_time"],
            merged_schedule["end_time"]
        )

        validate_schedule_dependencies(
            cursor=cursor,
            class_id=merged_schedule["class_id"],
            discipline_course_year_id=merged_schedule["discipline_course_year_id"],
            professor_id=merged_schedule["professor_id"],
            room_id=merged_schedule["room_id"],
            calendar_id=merged_schedule["calendar_id"]
        )

        validate_schedule_conflicts(
            cursor=cursor,
            class_id=merged_schedule["class_id"],
            professor_id=merged_schedule["professor_id"],
            room_id=merged_schedule["room_id"],
            calendar_id=merged_schedule["calendar_id"],
            start_time=merged_schedule["start_time"],
            end_time=merged_schedule["end_time"],
            excluded_schedule_id=schedule_id
        )

        field_map = {
            "class_id": "ClassID",
            "discipline_course_year_id": "DisciplineCourseYearID",
            "professor_id": "ProfessorID",
            "room_id": "RoomID",
            "calendar_id": "CalendarID",
            "start_time": "StartTime",
            "end_time": "EndTime",
            "status": "Status"
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

        values.append(schedule_id)

        cursor.execute(f"""
            UPDATE Tbl_GeneratedSchedule
            SET {", ".join(set_clauses)}
            WHERE ScheduleID = %s
        """, tuple(values))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Schedule record not found")

        return {
            "message": "Schedule record updated successfully",
            "schedule_id": schedule_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()
        connection.close()


@router.delete("/{schedule_id}")
def delete_schedule_record(
    schedule_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            DELETE FROM Tbl_GeneratedSchedule
            WHERE ScheduleID = %s
        """, (schedule_id,))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Schedule record not found")

        return {
            "message": "Schedule record deleted successfully",
            "schedule_id": schedule_id
        }

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="Schedule record cannot be deleted because it is being used by another record"
        )

    finally:
        cursor.close()
        connection.close()
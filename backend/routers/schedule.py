from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_db
from models import ScheduleCreate, ScheduleGenerateRequest, ScheduleUpdate
from services.schedule_generator import generate_schedule_algorithm
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


def get_class_for_generation(cursor, class_id: int):
    cursor.execute("""
        SELECT
            cl.ClassID AS class_id,
            cl.CourseID AS course_id,
            cl.SchoolYearID AS school_year_id,
            cl.CourseYearNumber AS course_year_number,
            COUNT(s.StudentID) AS class_size
        FROM Tbl_Classes cl
        LEFT JOIN Tbl_Students s
            ON cl.ClassID = s.ClassID
        WHERE cl.ClassID = %s
        GROUP BY
            cl.ClassID,
            cl.CourseID,
            cl.SchoolYearID,
            cl.CourseYearNumber
    """, (class_id,))

    class_data = cursor.fetchone()

    if class_data is None:
        raise HTTPException(status_code=404, detail="Class not found")

    if class_data["class_size"] == 0:
        class_data["class_size"] = 1

    return class_data


def get_disciplines_for_generation(cursor, class_data):
    cursor.execute("""
        SELECT
            dc.DisciplineCourseYearID AS discipline_course_year_id,
            d.Name AS discipline_name,
            dc.TotalMinutes AS total_minutes,
            dc.LessonDurationMinutes AS lesson_duration_minutes,
            dc.IsPractical AS is_practical
        FROM trx_Discipline_CourseYear dc
        JOIN Tbl_Disciplines d
            ON dc.DisciplineID = d.DisciplineID
        WHERE dc.CourseID = %s
          AND dc.SchoolYearID = %s
          AND dc.CourseYearNumber = %s
        ORDER BY d.Name
    """, (
        class_data["course_id"],
        class_data["school_year_id"],
        class_data["course_year_number"]
    ))

    disciplines = cursor.fetchall()

    if not disciplines:
        raise HTTPException(
            status_code=400,
            detail="No disciplines found for this class course year"
        )

    for discipline in disciplines:
        discipline["is_practical"] = bool(discipline["is_practical"])

    return disciplines


def get_school_days_for_generation(cursor, school_year_id: int, start_date, end_date):
    cursor.execute("""
        SELECT
            CalendarID AS calendar_id,
            CalendarDate AS date
        FROM Tbl_SchoolCalendar
        WHERE SchoolYearID = %s
          AND CalendarDate BETWEEN %s AND %s
          AND IsSchoolDay = 1
        ORDER BY CalendarDate
    """, (
        school_year_id,
        start_date,
        end_date
    ))

    school_days = cursor.fetchall()

    if not school_days:
        raise HTTPException(
            status_code=400,
            detail="No valid school days found for the selected date range"
        )

    return school_days


def get_professors_for_generation(cursor, discipline_course_year_ids):
    if not discipline_course_year_ids:
        return []

    placeholders = ", ".join(["%s"] * len(discipline_course_year_ids))

    cursor.execute(f"""
        SELECT
            ProfessorID AS professor_id,
            DisciplineCourseYearID AS discipline_course_year_id
        FROM trx_Professor_DisciplineCourseYear
        WHERE DisciplineCourseYearID IN ({placeholders})
    """, tuple(discipline_course_year_ids))

    professors = cursor.fetchall()

    if not professors:
        raise HTTPException(
            status_code=400,
            detail="No professors assigned to the selected disciplines"
        )

    return professors


def get_rooms_for_generation(cursor):
    cursor.execute("""
        SELECT
            RoomID AS room_id,
            COALESCE(Capacity, 999) AS capacity,
            IsPracticeRoom AS is_practical
        FROM Tbl_Rooms
        ORDER BY RoomID
    """)

    rooms = cursor.fetchall()

    if not rooms:
        raise HTTPException(
            status_code=400,
            detail="No rooms available"
        )

    for room in rooms:
        room["is_practical"] = bool(room["is_practical"])

    return rooms


def get_teacher_availability_for_generation(cursor, school_year_id: int):
    cursor.execute("""
        SELECT
            ProfessorID AS professor_id,
            DayOfWeek AS day_of_week,
            StartTime AS start_time,
            EndTime AS end_time
        FROM Tbl_TeacherAvailability
        WHERE SchoolYearID = %s
    """, (school_year_id,))

    rows = cursor.fetchall()

    day_map = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4
    }

    availability = []

    for row in rows:
        availability.append({
            "professor_id": row["professor_id"],
            "weekday": day_map[row["day_of_week"]],
            "start_time": row["start_time"],
            "end_time": row["end_time"]
        })

    return availability


def get_existing_schedule_for_generation(cursor, start_date, end_date, excluded_class_id=None):
    excluded_clause = ""
    values = [start_date, end_date]

    if excluded_class_id is not None:
        excluded_clause = "AND gs.ClassID <> %s"
        values.append(excluded_class_id)

    cursor.execute(f"""
        SELECT
            gs.ClassID AS class_id,
            gs.ProfessorID AS professor_id,
            gs.RoomID AS room_id,
            gs.CalendarID AS calendar_id,
            sc.CalendarDate AS date,
            gs.StartTime AS start_time,
            gs.EndTime AS end_time
        FROM Tbl_GeneratedSchedule gs
        JOIN Tbl_SchoolCalendar sc
            ON gs.CalendarID = sc.CalendarID
        WHERE sc.CalendarDate BETWEEN %s AND %s
          {excluded_clause}
    """, tuple(values))

    return cursor.fetchall()


def has_existing_schedule_for_class(cursor, class_id: int, start_date, end_date):
    cursor.execute("""
        SELECT 1
        FROM Tbl_GeneratedSchedule gs
        JOIN Tbl_SchoolCalendar sc
            ON gs.CalendarID = sc.CalendarID
        WHERE gs.ClassID = %s
          AND sc.CalendarDate BETWEEN %s AND %s
        LIMIT 1
    """, (
        class_id,
        start_date,
        end_date
    ))

    return cursor.fetchone() is not None


def delete_existing_schedule_for_class(cursor, class_id: int, start_date, end_date):
    cursor.execute("""
        DELETE gs
        FROM Tbl_GeneratedSchedule gs
        JOIN Tbl_SchoolCalendar sc
            ON gs.CalendarID = sc.CalendarID
        WHERE gs.ClassID = %s
          AND sc.CalendarDate BETWEEN %s AND %s
    """, (
        class_id,
        start_date,
        end_date
    ))


@router.post("/generate")
def generate_schedule(
    request: ScheduleGenerateRequest,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    if request.end_date < request.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be greater than or equal to start date"
        )

    validate_time_range(request.school_start, request.school_end)

    cursor = connection.cursor(dictionary=True)
    audit_username = get_audit_username(current_user)

    try:
        if request.replace_existing and not request.dry_run:
            delete_existing_schedule_for_class(
                cursor=cursor,
                class_id=request.class_id,
                start_date=request.start_date,
                end_date=request.end_date
            )
        elif not request.replace_existing:
            if has_existing_schedule_for_class(
                cursor=cursor,
                class_id=request.class_id,
                start_date=request.start_date,
                end_date=request.end_date
            ):
                raise HTTPException(
                    status_code=409,
                    detail="Schedule already exists for this class in the selected date range. Use replace_existing=true to regenerate it."
                )

        class_data = get_class_for_generation(
            cursor=cursor,
            class_id=request.class_id
        )

        disciplines = get_disciplines_for_generation(
            cursor=cursor,
            class_data=class_data
        )

        school_days = get_school_days_for_generation(
            cursor=cursor,
            school_year_id=class_data["school_year_id"],
            start_date=request.start_date,
            end_date=request.end_date
        )

        discipline_course_year_ids = [
            discipline["discipline_course_year_id"]
            for discipline in disciplines
        ]

        professors = get_professors_for_generation(
            cursor=cursor,
            discipline_course_year_ids=discipline_course_year_ids
        )

        rooms = get_rooms_for_generation(cursor)

        teacher_availability = get_teacher_availability_for_generation(
            cursor=cursor,
            school_year_id=class_data["school_year_id"]
        )

        if not teacher_availability:
            raise HTTPException(
                status_code=400,
                detail="No teacher availability records found for this school year"
            )

        existing_schedule = get_existing_schedule_for_generation(
            cursor=cursor,
            start_date=request.start_date,
            end_date=request.end_date,
            excluded_class_id=request.class_id if request.replace_existing else None
        )

        result = generate_schedule_algorithm(
            class_data=class_data,
            disciplines=disciplines,
            school_days=school_days,
            professors=professors,
            rooms=rooms,
            teacher_availability=teacher_availability,
            existing_schedule=existing_schedule,
            school_start=request.school_start,
            school_end=request.school_end,
            max_sessions_per_discipline=request.max_sessions_per_discipline,
            max_total_sessions=request.max_total_sessions
        )

        if not result["success"]:
            connection.rollback()
            return {
                "message": "Schedule generation failed",
                "created_records": 0,
                "score": result["score"],
                "conflicts": result["conflicts"],
                "stats": result.get("stats", {}),
                "generation_settings": {
                    "school_start": request.school_start,
                    "school_end": request.school_end,
                    "max_sessions_per_discipline": request.max_sessions_per_discipline,
                    "max_total_sessions": request.max_total_sessions,
                    "dry_run": request.dry_run
                }
            }

        if request.dry_run:
            connection.rollback()
            return {
                "message": "Schedule generated successfully (dry run, not saved)",
                "created_records": result["created_records"],
                "score": result["score"],
                "conflicts": result["conflicts"],
                "stats": result.get("stats", {}),
                "generation_settings": {
                    "school_start": request.school_start,
                    "school_end": request.school_end,
                    "max_sessions_per_discipline": request.max_sessions_per_discipline,
                    "max_total_sessions": request.max_total_sessions,
                    "dry_run": request.dry_run
                },
                "schedule_preview": result["schedule"]
            }

        for record in result["schedule"]:
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
                record["class_id"],
                record["discipline_course_year_id"],
                record["professor_id"],
                record["room_id"],
                record["calendar_id"],
                record["start_time"],
                record["end_time"],
                request.status,
                audit_username
            ))

        connection.commit()

        return {
            "message": "Schedule generated successfully",
            "created_records": result["created_records"],
            "score": result["score"],
            "conflicts": result["conflicts"],
            "stats": result.get("stats", {}),
            "generation_settings": {
                "school_start": request.school_start,
                "school_end": request.school_end,
                "max_sessions_per_discipline": request.max_sessions_per_discipline,
                "max_total_sessions": request.max_total_sessions,
                "dry_run": request.dry_run,
                "status": request.status
            }
        }

    except HTTPException:
        connection.rollback()
        raise

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.get("")
def get_schedule(
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
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


@router.get("/class/{class_id}")
def get_schedule_by_class(
    class_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
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


@router.get("/professor/{professor_id}")
def get_schedule_by_professor(
    professor_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
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


@router.get("/room/{room_id}")
def get_schedule_by_room(
    room_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
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


@router.get("/{schedule_id}")
def get_schedule_record(
    schedule_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
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


@router.post("")
def create_schedule_record(
    schedule: ScheduleCreate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    validate_time_range(schedule.start_time, schedule.end_time)

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


@router.put("/{schedule_id}")
def update_schedule_record(
    schedule_id: int,
    schedule: ScheduleUpdate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    data = model_to_dict(schedule)

    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

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


@router.delete("/{schedule_id}")
def delete_schedule_record(
    schedule_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
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
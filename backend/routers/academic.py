from fastapi import APIRouter, Depends

from db import get_connection
from auth import require_roles


router = APIRouter(tags=["Academic Data"])


@router.get("/professors")
def get_professors(
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            id,
            full_name,
            email
        FROM professors
    """)

    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data


@router.get("/rooms")
def get_rooms(
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            id,
            name,
            capacity,
            is_practice_room,
            location
        FROM rooms
    """)

    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data


@router.get("/disciplines")
def get_disciplines(
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            id,
            name,
            total_hours,
            lesson_duration_minutes,
            is_practical
        FROM disciplines
    """)

    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data


@router.get("/schedule")
def get_schedule(
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            generated_schedule.id,
            generated_schedule.schedule_date,
            generated_schedule.start_time,
            generated_schedule.end_time,
            classes.name AS class_name,
            disciplines.name AS discipline,
            professors.full_name AS professor,
            rooms.name AS room,
            generated_schedule.status
        FROM generated_schedule
        JOIN classes ON generated_schedule.class_id = classes.id
        JOIN disciplines ON generated_schedule.discipline_id = disciplines.id
        JOIN professors ON generated_schedule.professor_id = professors.id
        JOIN rooms ON generated_schedule.room_id = rooms.id
    """)

    data = cursor.fetchall()

    for item in data:
        item["schedule_date"] = str(item["schedule_date"])
        item["start_time"] = str(item["start_time"])
        item["end_time"] = str(item["end_time"])

    cursor.close()
    connection.close()

    return data
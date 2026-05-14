from fastapi import APIRouter, HTTPException, Depends

from db import get_connection
from auth import require_roles
from models import RoomCreate, RoomUpdate


router = APIRouter(prefix="/rooms", tags=["Rooms"])


def validate_capacity(capacity):
    if capacity is not None and capacity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Room capacity must be greater than 0"
        )


@router.get("")
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


@router.post("")
def create_room(
    room: RoomCreate,
    current_user=Depends(require_roles(["admin", "secretary"]))
):
    validate_capacity(room.capacity)

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        INSERT INTO rooms
        (name, capacity, is_practice_room, location)
        VALUES (%s, %s, %s, %s)
        """,
        (
            room.name,
            room.capacity,
            room.is_practice_room,
            room.location
        )
    )

    connection.commit()
    new_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return {
        "message": "Room created successfully",
        "room_id": new_id
    }


@router.put("/{room_id}")
def update_room(
    room_id: int,
    room: RoomUpdate,
    current_user=Depends(require_roles(["admin", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM rooms WHERE id = %s",
        (room_id,)
    )

    existing_room = cursor.fetchone()

    if existing_room is None:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Room not found")

    update_fields = []
    values = []

    if room.name is not None:
        update_fields.append("name = %s")
        values.append(room.name)

    if room.capacity is not None:
        validate_capacity(room.capacity)
        update_fields.append("capacity = %s")
        values.append(room.capacity)

    if room.is_practice_room is not None:
        update_fields.append("is_practice_room = %s")
        values.append(room.is_practice_room)

    if room.location is not None:
        update_fields.append("location = %s")
        values.append(room.location)

    if not update_fields:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=400, detail="No fields to update")

    values.append(room_id)

    cursor.execute(
        f"""
        UPDATE rooms
        SET {", ".join(update_fields)}
        WHERE id = %s
        """,
        values
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Room updated successfully",
        "room_id": room_id
    }


@router.delete("/{room_id}")
def delete_room(
    room_id: int,
    current_user=Depends(require_roles(["admin", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM rooms WHERE id = %s",
        (room_id,)
    )

    room = cursor.fetchone()

    if room is None:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Room not found")

    cursor.execute(
        "SELECT id FROM generated_schedule WHERE room_id = %s LIMIT 1",
        (room_id,)
    )

    schedule = cursor.fetchone()

    if schedule is not None:
        cursor.close()
        connection.close()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete room with generated schedules"
        )

    cursor.execute(
        "DELETE FROM rooms WHERE id = %s",
        (room_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Room deleted successfully",
        "room_id": room_id
    }
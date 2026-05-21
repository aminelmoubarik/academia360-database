from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_db
from models import RoomCreate, RoomUpdate
from utils import get_audit_username, model_to_dict

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("")
def get_rooms(
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                RoomID AS id,
                Name AS name,
                Capacity AS capacity,
                IsPracticeRoom AS is_practice_room,
                Location AS location,
                InsertUsername AS insert_username,
                InsertDate AS insert_date,
                ChangeUsername AS change_username,
                ChangeDate AS change_date
            FROM Tbl_Rooms
            ORDER BY RoomID
        """)

        return cursor.fetchall()

    finally:
        cursor.close()


@router.get("/{room_id}")
def get_room(
    room_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                RoomID AS id,
                Name AS name,
                Capacity AS capacity,
                IsPracticeRoom AS is_practice_room,
                Location AS location,
                InsertUsername AS insert_username,
                InsertDate AS insert_date,
                ChangeUsername AS change_username,
                ChangeDate AS change_date
            FROM Tbl_Rooms
            WHERE RoomID = %s
        """, (room_id,))

        room = cursor.fetchone()

        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")

        return room

    finally:
        cursor.close()


@router.post("")
def create_room(
    room: RoomCreate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        cursor.execute("""
            INSERT INTO Tbl_Rooms (
                Name,
                Capacity,
                IsPracticeRoom,
                Location,
                InsertUsername
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            room.name,
            room.capacity,
            room.is_practice_room,
            room.location,
            audit_username
        ))

        connection.commit()

        return {
            "message": "Room created successfully",
            "room_id": cursor.lastrowid
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.put("/{room_id}")
def update_room(
    room_id: int,
    room: RoomUpdate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    data = model_to_dict(room)

    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    field_map = {
        "name": "Name",
        "capacity": "Capacity",
        "is_practice_room": "IsPracticeRoom",
        "location": "Location"
    }

    set_clauses = []
    values = []

    for api_field, db_field in field_map.items():
        if api_field in data:
            set_clauses.append(f"{db_field} = %s")
            values.append(data[api_field])

    if not set_clauses:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")

    audit_username = get_audit_username(current_user)

    set_clauses.append("ChangeUsername = %s")
    values.append(audit_username)

    values.append(room_id)

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"""
            UPDATE Tbl_Rooms
            SET {", ".join(set_clauses)}
            WHERE RoomID = %s
        """, tuple(values))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Room not found")

        return {
            "message": "Room updated successfully",
            "room_id": room_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.delete("/{room_id}")
def delete_room(
    room_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            DELETE FROM Tbl_Rooms
            WHERE RoomID = %s
        """, (room_id,))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Room not found")

        return {
            "message": "Room deleted successfully",
            "room_id": room_id
        }

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="Room cannot be deleted because it is being used by another record"
        )

    finally:
        cursor.close()
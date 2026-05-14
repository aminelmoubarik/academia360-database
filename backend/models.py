from typing import Optional, Literal

from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class AttendanceCreate(BaseModel):
    student_id: int
    schedule_id: Optional[int] = None
    punch_type: Literal["in", "out"]
    punch_method: Literal["nfc", "rfid", "qr", "barcode", "manual"]


class StudentCreate(BaseModel):
    full_name: str
    student_number: Optional[str] = None
    card_uid: Optional[str] = None
    class_id: Optional[int] = None


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    student_number: Optional[str] = None
    card_uid: Optional[str] = None
    class_id: Optional[int] = None


class ProfessorCreate(BaseModel):
    user_id: Optional[int] = None
    full_name: str
    email: str


class ProfessorUpdate(BaseModel):
    user_id: Optional[int] = None
    full_name: Optional[str] = None
    email: Optional[str] = None

class RoomCreate(BaseModel):
    name: str
    capacity: Optional[int] = None
    is_practice_room: bool = False
    location: Optional[str] = None


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    is_practice_room: Optional[bool] = None
    location: Optional[str] = None
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
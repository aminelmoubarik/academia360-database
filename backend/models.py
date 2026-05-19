from datetime import date, time
from typing import Literal, Optional

from pydantic import BaseModel


# ============================================================
# REFERENCE TABLES
# ============================================================

class RoleCreate(BaseModel):
    name: str


class RoleUpdate(BaseModel):
    name: Optional[str] = None


class GenderCreate(BaseModel):
    name: str


class GenderUpdate(BaseModel):
    name: Optional[str] = None


class SchoolYearCreate(BaseModel):
    name: str
    start_date: date
    end_date: date


class SchoolYearUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


# ============================================================
# USERS
# ============================================================

class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    role_id: int


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None


# ============================================================
# COURSES
# ============================================================

class CourseCreate(BaseModel):
    code: str
    name: str


class CourseUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None


# ============================================================
# CLASSES
# ============================================================

class ClassCreate(BaseModel):
    name: str
    course_id: int
    school_year_id: int
    course_year_number: int


class ClassUpdate(BaseModel):
    name: Optional[str] = None
    course_id: Optional[int] = None
    school_year_id: Optional[int] = None
    course_year_number: Optional[int] = None


# ============================================================
# STUDENTS
# ============================================================

class StudentCreate(BaseModel):
    full_name: str
    student_number: Optional[str] = None
    card_uid: Optional[str] = None
    class_id: Optional[int] = None
    photo_path: Optional[str] = None
    gender_id: Optional[int] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    contact: Optional[str] = None
    date_of_birth: Optional[date] = None


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    student_number: Optional[str] = None
    card_uid: Optional[str] = None
    class_id: Optional[int] = None
    photo_path: Optional[str] = None
    gender_id: Optional[int] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    contact: Optional[str] = None
    date_of_birth: Optional[date] = None


# ============================================================
# PROFESSORS
# ============================================================

class ProfessorCreate(BaseModel):
    user_id: int
    photo_path: Optional[str] = None
    gender_id: Optional[int] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    contact: Optional[str] = None
    date_of_birth: Optional[date] = None


class ProfessorUpdate(BaseModel):
    user_id: Optional[int] = None
    photo_path: Optional[str] = None
    gender_id: Optional[int] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    contact: Optional[str] = None
    date_of_birth: Optional[date] = None


# ============================================================
# DISCIPLINES
# ============================================================

class DisciplineCreate(BaseModel):
    name: str
    code: Optional[str] = None


class DisciplineUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None


# ============================================================
# DISCIPLINE COURSE YEARS
# ============================================================

class DisciplineCourseYearCreate(BaseModel):
    discipline_id: int
    course_id: int
    school_year_id: int
    course_year_number: int
    total_minutes: int
    lesson_duration_minutes: int = 60
    is_practical: bool = False


class DisciplineCourseYearUpdate(BaseModel):
    discipline_id: Optional[int] = None
    course_id: Optional[int] = None
    school_year_id: Optional[int] = None
    course_year_number: Optional[int] = None
    total_minutes: Optional[int] = None
    lesson_duration_minutes: Optional[int] = None
    is_practical: Optional[bool] = None


class ProfessorDisciplineCourseYearCreate(BaseModel):
    professor_id: int
    discipline_course_year_id: int


# ============================================================
# ROOMS
# ============================================================

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


# ============================================================
# SCHOOL CALENDAR
# ============================================================

class SchoolCalendarCreate(BaseModel):
    school_year_id: int
    calendar_date: date
    is_school_day: bool = True
    description: Optional[str] = None


class SchoolCalendarUpdate(BaseModel):
    school_year_id: Optional[int] = None
    calendar_date: Optional[date] = None
    is_school_day: Optional[bool] = None
    description: Optional[str] = None


# ============================================================
# TEACHER AVAILABILITY
# ============================================================

class TeacherAvailabilityCreate(BaseModel):
    professor_id: int
    school_year_id: int
    day_of_week: Literal["monday", "tuesday", "wednesday", "thursday", "friday"]
    start_time: time
    end_time: time


class TeacherAvailabilityUpdate(BaseModel):
    professor_id: Optional[int] = None
    school_year_id: Optional[int] = None
    day_of_week: Optional[Literal["monday", "tuesday", "wednesday", "thursday", "friday"]] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None


# ============================================================
# SCHEDULE
# ============================================================

class ScheduleCreate(BaseModel):
    class_id: int
    discipline_course_year_id: int
    professor_id: int
    room_id: int
    calendar_id: int
    start_time: time
    end_time: time
    status: Literal["draft", "approved", "cancelled"] = "draft"


class ScheduleUpdate(BaseModel):
    class_id: Optional[int] = None
    discipline_course_year_id: Optional[int] = None
    professor_id: Optional[int] = None
    room_id: Optional[int] = None
    calendar_id: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    status: Optional[Literal["draft", "approved", "cancelled"]] = None


# ============================================================
# ATTENDANCE
# ============================================================

class AttendanceCreate(BaseModel):
    student_id: int
    schedule_id: Optional[int] = None
    punch_type: Literal["in", "out"]
    punch_method: Literal["nfc", "rfid", "qr", "barcode", "manual"]
    is_synced: bool = True


class AttendanceUpdate(BaseModel):
    student_id: Optional[int] = None
    schedule_id: Optional[int] = None
    punch_type: Optional[Literal["in", "out"]] = None
    punch_method: Optional[Literal["nfc", "rfid", "qr", "barcode", "manual"]] = None
    is_synced: Optional[bool] = None


# ============================================================
# AUTH
# ============================================================

class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
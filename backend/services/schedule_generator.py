import math
from datetime import datetime, time, timedelta


MAX_BACKTRACK_ATTEMPTS = 100000


def normalize_time(value):
    if isinstance(value, time):
        return value

    if isinstance(value, datetime):
        return value.time()

    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return time(hour=hours, minute=minutes, second=seconds)

    return value


def time_to_minutes(value):
    value = normalize_time(value)
    return value.hour * 60 + value.minute


def time_overlaps(start_a, end_a, start_b, end_b):
    start_a = time_to_minutes(start_a)
    end_a = time_to_minutes(end_a)
    start_b = time_to_minutes(start_b)
    end_b = time_to_minutes(end_b)

    return start_a < end_b and end_a > start_b


def calculate_sessions_needed(total_minutes, lesson_duration_minutes):
    return math.ceil(total_minutes / lesson_duration_minutes)


def generate_time_slots(school_days, lesson_duration_minutes, school_start, school_end):
    slots = []

    for day in school_days:
        current_time = datetime.combine(day["date"], normalize_time(school_start))
        end_of_day = datetime.combine(day["date"], normalize_time(school_end))

        while current_time + timedelta(minutes=lesson_duration_minutes) <= end_of_day:
            slot_start = current_time.time()
            slot_end = (current_time + timedelta(minutes=lesson_duration_minutes)).time()

            slots.append({
                "calendar_id": day["calendar_id"],
                "date": day["date"],
                "start_time": slot_start,
                "end_time": slot_end
            })

            current_time += timedelta(minutes=lesson_duration_minutes)

    return slots


def is_teacher_available(candidate, teacher_availability):
    professor_id = candidate["professor_id"]
    weekday = candidate["date"].weekday()
    start_time = time_to_minutes(candidate["start_time"])
    end_time = time_to_minutes(candidate["end_time"])

    for availability in teacher_availability:
        if availability["professor_id"] != professor_id:
            continue

        if availability["weekday"] != weekday:
            continue

        availability_start = time_to_minutes(availability["start_time"])
        availability_end = time_to_minutes(availability["end_time"])

        if availability_start <= start_time and availability_end >= end_time:
            return True

    return False


def has_teacher_conflict(candidate, schedules):
    for schedule in schedules:
        if schedule["professor_id"] != candidate["professor_id"]:
            continue

        if schedule["date"] != candidate["date"]:
            continue

        if time_overlaps(
            candidate["start_time"],
            candidate["end_time"],
            schedule["start_time"],
            schedule["end_time"]
        ):
            return True

    return False


def has_class_conflict(candidate, schedules):
    for schedule in schedules:
        if schedule["class_id"] != candidate["class_id"]:
            continue

        if schedule["date"] != candidate["date"]:
            continue

        if time_overlaps(
            candidate["start_time"],
            candidate["end_time"],
            schedule["start_time"],
            schedule["end_time"]
        ):
            return True

    return False


def has_room_conflict(candidate, schedules):
    for schedule in schedules:
        if schedule["room_id"] != candidate["room_id"]:
            continue

        if schedule["date"] != candidate["date"]:
            continue

        if time_overlaps(
            candidate["start_time"],
            candidate["end_time"],
            schedule["start_time"],
            schedule["end_time"]
        ):
            return True

    return False


def is_valid_candidate(candidate, existing_schedule, temporary_solution, teacher_availability):
    all_schedules = existing_schedule + temporary_solution

    if candidate["room_capacity"] < candidate["class_size"]:
        return False

    if candidate["is_practical"] and not candidate["room_is_practical"]:
        return False

    if not is_teacher_available(candidate, teacher_availability):
        return False

    if has_teacher_conflict(candidate, all_schedules):
        return False

    if has_class_conflict(candidate, all_schedules):
        return False

    if has_room_conflict(candidate, all_schedules):
        return False

    return True


def calculate_candidate_score(candidate, temporary_solution):
    score = 100

    same_day_class_lessons = [
        schedule for schedule in temporary_solution
        if schedule["class_id"] == candidate["class_id"]
        and schedule["date"] == candidate["date"]
    ]

    same_day_teacher_lessons = [
        schedule for schedule in temporary_solution
        if schedule["professor_id"] == candidate["professor_id"]
        and schedule["date"] == candidate["date"]
    ]

    same_day_same_discipline = [
        schedule for schedule in temporary_solution
        if schedule["class_id"] == candidate["class_id"]
        and schedule["discipline_course_year_id"] == candidate["discipline_course_year_id"]
        and schedule["date"] == candidate["date"]
    ]

    if same_day_same_discipline:
        score -= 25

    if len(same_day_class_lessons) >= 4:
        score -= 15

    if len(same_day_teacher_lessons) >= 4:
        score -= 15

    if candidate["is_practical"] and candidate["room_is_practical"]:
        score += 10

    if candidate["room_capacity"] <= candidate["class_size"] + 5:
        score += 5

    if candidate["room_capacity"] > candidate["class_size"] * 2:
        score -= 5

    return score


def generate_candidates(session, time_slots, professors, rooms):
    candidates = []

    valid_professors = [
        professor for professor in professors
        if professor["discipline_course_year_id"] == session["discipline_course_year_id"]
    ]

    valid_rooms = [
        room for room in rooms
        if room["capacity"] >= session["class_size"]
        and (not session["is_practical"] or room["is_practical"])
    ]

    for slot in time_slots:
        for professor in valid_professors:
            for room in valid_rooms:
                candidates.append({
                    "class_id": session["class_id"],
                    "class_size": session["class_size"],
                    "discipline_course_year_id": session["discipline_course_year_id"],
                    "discipline_name": session["discipline_name"],
                    "session_number": session["session_number"],
                    "professor_id": professor["professor_id"],
                    "room_id": room["room_id"],
                    "room_capacity": room["capacity"],
                    "room_is_practical": room["is_practical"],
                    "calendar_id": slot["calendar_id"],
                    "date": slot["date"],
                    "start_time": slot["start_time"],
                    "end_time": slot["end_time"],
                    "is_practical": session["is_practical"]
                })

    return candidates


def sort_sessions_by_difficulty(sessions, professors, rooms):
    def difficulty(session):
        professor_count = len([
            professor for professor in professors
            if professor["discipline_course_year_id"] == session["discipline_course_year_id"]
        ])

        room_count = len([
            room for room in rooms
            if room["capacity"] >= session["class_size"]
            and (not session["is_practical"] or room["is_practical"])
        ])

        return (
            1 if session["is_practical"] else 0,
            -professor_count,
            -room_count,
            session["lesson_duration_minutes"],
            session["total_minutes"]
        )

    return sorted(sessions, key=difficulty, reverse=True)


def build_pending_sessions(class_data, disciplines, max_sessions_per_discipline=None):
    pending_sessions = []

    for discipline in disciplines:
        sessions_needed = calculate_sessions_needed(
            total_minutes=discipline["total_minutes"],
            lesson_duration_minutes=discipline["lesson_duration_minutes"]
        )

        if max_sessions_per_discipline is not None:
            sessions_needed = min(sessions_needed, max_sessions_per_discipline)

        for session_number in range(sessions_needed):
            pending_sessions.append({
                "class_id": class_data["class_id"],
                "class_size": class_data["class_size"],
                "discipline_course_year_id": discipline["discipline_course_year_id"],
                "discipline_name": discipline["discipline_name"],
                "total_minutes": discipline["total_minutes"],
                "lesson_duration_minutes": discipline["lesson_duration_minutes"],
                "is_practical": discipline["is_practical"],
                "session_number": session_number + 1
            })

    return pending_sessions


def find_input_conflicts(class_data, disciplines, professors, rooms):
    conflicts = []

    for discipline in disciplines:
        assigned_professors = [
            professor for professor in professors
            if professor["discipline_course_year_id"] == discipline["discipline_course_year_id"]
        ]

        valid_rooms = [
            room for room in rooms
            if room["capacity"] >= class_data["class_size"]
            and (not discipline["is_practical"] or room["is_practical"])
        ]

        if not assigned_professors:
            conflicts.append({
                "class_id": class_data["class_id"],
                "discipline": discipline["discipline_name"],
                "reason": "No professor is assigned to this discipline course year"
            })

        if not valid_rooms:
            conflicts.append({
                "class_id": class_data["class_id"],
                "discipline": discipline["discipline_name"],
                "reason": "No room has enough capacity or the required practical-room type"
            })

        if discipline["lesson_duration_minutes"] <= 0:
            conflicts.append({
                "class_id": class_data["class_id"],
                "discipline": discipline["discipline_name"],
                "reason": "Lesson duration must be greater than zero"
            })

    return conflicts


def build_valid_candidates(
    session,
    time_slots,
    professors,
    rooms,
    existing_schedule,
    temporary_solution,
    teacher_availability
):
    valid_candidates = []

    for candidate in generate_candidates(
        session=session,
        time_slots=time_slots,
        professors=professors,
        rooms=rooms
    ):
        if is_valid_candidate(
            candidate=candidate,
            existing_schedule=existing_schedule,
            temporary_solution=temporary_solution,
            teacher_availability=teacher_availability
        ):
            candidate["score"] = calculate_candidate_score(
                candidate=candidate,
                temporary_solution=temporary_solution
            )
            valid_candidates.append(candidate)

    valid_candidates.sort(key=lambda item: item["score"], reverse=True)
    return valid_candidates


def solve_with_backtracking(
    pending_sessions,
    time_slots_by_duration,
    professors,
    rooms,
    teacher_availability,
    existing_schedule,
    max_attempts=MAX_BACKTRACK_ATTEMPTS
):
    if not pending_sessions:
        return True, [], [], 0

    temporary_solution = []
    candidate_stack = []
    candidate_index_stack = []
    session_index = 0
    attempts = 0
    last_failed_session = None

    while session_index < len(pending_sessions):
        if attempts >= max_attempts:
            return False, temporary_solution, [{
                "class_id": pending_sessions[session_index]["class_id"],
                "discipline": pending_sessions[session_index]["discipline_name"],
                "reason": f"Maximum backtracking attempts reached ({max_attempts})"
            }], attempts

        if session_index == len(candidate_stack):
            session = pending_sessions[session_index]
            time_slots = time_slots_by_duration[session["lesson_duration_minutes"]]

            candidates = build_valid_candidates(
                session=session,
                time_slots=time_slots,
                professors=professors,
                rooms=rooms,
                existing_schedule=existing_schedule,
                temporary_solution=temporary_solution,
                teacher_availability=teacher_availability
            )

            if not candidates:
                last_failed_session = session

                if session_index == 0:
                    return False, temporary_solution, [{
                        "class_id": session["class_id"],
                        "discipline": session["discipline_name"],
                        "session_number": session["session_number"],
                        "reason": "No valid slot found"
                    }], attempts

                session_index -= 1
                temporary_solution.pop()
                candidate_index_stack[session_index] += 1
                continue

            candidate_stack.append(candidates)
            candidate_index_stack.append(0)

        if candidate_index_stack[session_index] >= len(candidate_stack[session_index]):
            last_failed_session = pending_sessions[session_index]
            candidate_stack.pop()
            candidate_index_stack.pop()

            if session_index == 0:
                reason = "No valid complete schedule found after trying all candidates"
                if last_failed_session is not None:
                    return False, temporary_solution, [{
                        "class_id": last_failed_session["class_id"],
                        "discipline": last_failed_session["discipline_name"],
                        "session_number": last_failed_session["session_number"],
                        "reason": reason
                    }], attempts

                return False, temporary_solution, [{"reason": reason}], attempts

            session_index -= 1
            temporary_solution.pop()
            candidate_index_stack[session_index] += 1
            continue

        candidate = candidate_stack[session_index][candidate_index_stack[session_index]]
        temporary_solution.append(candidate)
        attempts += 1
        session_index += 1

    return True, temporary_solution, [], attempts


def generate_schedule_algorithm(
    class_data,
    disciplines,
    school_days,
    professors,
    rooms,
    teacher_availability,
    existing_schedule,
    school_start,
    school_end,
    max_sessions_per_discipline=None,
    max_total_sessions=300,
    max_attempts=MAX_BACKTRACK_ATTEMPTS
):
    input_conflicts = find_input_conflicts(
        class_data=class_data,
        disciplines=disciplines,
        professors=professors,
        rooms=rooms
    )

    if input_conflicts:
        return {
            "success": False,
            "created_records": 0,
            "score": 0,
            "schedule": [],
            "conflicts": input_conflicts,
            "stats": {
                "pending_sessions": 0,
                "school_days": len(school_days),
                "attempts": 0
            }
        }

    pending_sessions = build_pending_sessions(
        class_data=class_data,
        disciplines=disciplines,
        max_sessions_per_discipline=max_sessions_per_discipline
    )

    if len(pending_sessions) > max_total_sessions:
        return {
            "success": False,
            "created_records": 0,
            "score": 0,
            "schedule": [],
            "conflicts": [{
                "class_id": class_data["class_id"],
                "reason": (
                    f"Too many sessions requested ({len(pending_sessions)}). "
                    f"Limit is {max_total_sessions}. Use a wider date range, reduce workload, "
                    "or use max_sessions_per_discipline for testing."
                )
            }],
            "stats": {
                "pending_sessions": len(pending_sessions),
                "school_days": len(school_days),
                "attempts": 0
            }
        }

    pending_sessions = sort_sessions_by_difficulty(
        sessions=pending_sessions,
        professors=professors,
        rooms=rooms
    )

    time_slots_by_duration = {}

    for session in pending_sessions:
        duration = session["lesson_duration_minutes"]

        if duration not in time_slots_by_duration:
            time_slots_by_duration[duration] = generate_time_slots(
                school_days=school_days,
                lesson_duration_minutes=duration,
                school_start=school_start,
                school_end=school_end
            )

            if not time_slots_by_duration[duration]:
                return {
                    "success": False,
                    "created_records": 0,
                    "score": 0,
                    "schedule": [],
                    "conflicts": [{
                        "class_id": session["class_id"],
                        "discipline": session["discipline_name"],
                        "reason": "No time slots available for this lesson duration"
                    }],
                    "stats": {
                        "pending_sessions": len(pending_sessions),
                        "school_days": len(school_days),
                        "attempts": 0
                    }
                }

    success, temporary_solution, conflicts, attempts = solve_with_backtracking(
        pending_sessions=pending_sessions,
        time_slots_by_duration=time_slots_by_duration,
        professors=professors,
        rooms=rooms,
        teacher_availability=teacher_availability,
        existing_schedule=existing_schedule,
        max_attempts=max_attempts
    )

    total_score = sum(
        item["score"]
        for item in temporary_solution
        if "score" in item
    )

    return {
        "success": success,
        "created_records": len(temporary_solution),
        "score": total_score,
        "schedule": temporary_solution,
        "conflicts": conflicts,
        "stats": {
            "pending_sessions": len(pending_sessions),
            "school_days": len(school_days),
            "attempts": attempts,
            "time_slots_by_duration": {
                str(duration): len(slots)
                for duration, slots in time_slots_by_duration.items()
            }
        }
    }

import re
from datetime import datetime, date

from src.utils.enums import Role


def valid_email(email: str):
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


def valid_phone(phone):
    if not phone:
        return True
    return re.fullmatch(r"\d{10}", phone) is not None


def valid_password(password):
    if len(password) < 8:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"\d", password):
        return False

    return True


def valid_dob(dob_string):
    if not dob_string:
        return False

    dob = datetime.strptime(dob_string, "%Y-%m-%d").date()
    today = date.today()

    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    return age >= 15


def to_int(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def validate_user_create_form(form):
    required_text_fields = ["first_name", "last_name", "address"]
    for field in required_text_fields:
        if not form.get(field, "").strip():
            return f"{field.replace('_', ' ').title()} is required."

    email = form.get("email", "").strip().lower()
    if not valid_email(email):
        return "Invalid email format."

    password = form.get("password", "").strip()
    if not valid_password(password):
        return "Password must be 8+ chars with uppercase, lowercase, and number."

    phone = form.get("phone", "").strip()
    if not valid_phone(phone):
        return "Phone number must be exactly 10 digits."

    dob = form.get("dob", "").strip()
    if not valid_dob(dob):
        return "DOB is invalid. User must be at least 15 years old."

    gender = form.get("gender", "").strip()
    if gender not in {"m", "f", "o"}:
        return "Invalid gender."

    role = form.get("role", "").strip()
    if role not in {r.value for r in Role}:
        return "Invalid role."

    if role == Role.ARTIST.value:
        if not form.get("stage_name", "").strip():
            return "Stage name is required for artist role."
        release_year = to_int(form.get("first_release_year"))
        if release_year is None:
            return "First release year must be a valid number."
        if release_year < 1900 or release_year > date.today().year:
            return "First release year is out of valid range."

        albums = to_int(form.get("no_of_albums_released"))
        if albums is None or albums < 0:
            return "No. of albums released must be 0 or greater."

    return ""


def validate_artist_create_form(form):
    required_text_fields = [
        "first_name",
        "last_name",
        "address",
        "stage_name",
    ]
    for field in required_text_fields:
        if not form.get(field, "").strip():
            return f"{field.replace('_', ' ').title()} is required."

    email = form.get("email", "").strip().lower()
    if not valid_email(email):
        return "Invalid email format."

    password = form.get("password", "").strip()
    if not valid_password(password):
        return "Password must be 8+ chars with uppercase, lowercase, and number."

    phone = form.get("phone", "").strip()
    if not valid_phone(phone):
        return "Phone number must be exactly 10 digits."

    dob = form.get("dob", "").strip()
    if not valid_dob(dob):
        return "DOB is invalid. User must be at least 15 years old."

    gender = form.get("gender", "").strip()
    if gender not in {"m", "f", "o"}:
        return "Invalid gender."

    release_year = to_int(form.get("first_release_year"))
    if release_year is None:
        return "First release year must be a valid number."
    if release_year < 1900 or release_year > date.today().year:
        return "First release year is out of valid range."

    albums = to_int(form.get("no_of_albums_released"))
    if albums is None or albums < 0:
        return "No. of albums released must be 0 or greater."

    return ""

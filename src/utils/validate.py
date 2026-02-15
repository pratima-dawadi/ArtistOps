import re
from datetime import datetime, date


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

import re


def valid_email(email: str):
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None

import secrets
from http import HTTPStatus

SESSION_COOKIE_NAME = "ams_session_id"
_SESSIONS = {}


def parse_cookies(cookie_header):
    cookies = {}
    if not cookie_header:
        return cookies

    for chunk in cookie_header.split(";"):
        part = chunk.strip()
        if not part or "=" not in part:
            continue
        key, value = part.split("=", 1)
        cookies[key] = value
    return cookies


def get_session_id(handler):
    cookie_header = handler.headers.get("Cookie", "")
    cookies = parse_cookies(cookie_header)
    return cookies.get(SESSION_COOKIE_NAME)


def get_user_from_session(handler):
    session_id = get_session_id(handler)
    if not session_id:
        return None
    return _SESSIONS.get(session_id)


def create_session(user):
    session_id = secrets.token_urlsafe(32)
    _SESSIONS[session_id] = {
        "id": user.get("id"),
        "email": user.get("email"),
        "role": user.get("role"),
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
    }
    return session_id


def destroy_session(session_id):
    if session_id:
        _SESSIONS.pop(session_id, None)


def require_login(handler):
    if get_user_from_session(handler):
        return True
    handler.send_response(HTTPStatus.SEE_OTHER)
    handler.send_header("Location", "/login")
    handler.end_headers()
    return False

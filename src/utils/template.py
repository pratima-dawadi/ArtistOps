import os
from urllib.parse import parse_qs

TEMPLATE_DIR = os.path.join("templates")


def render_template(template_name, **context):
    file_path = os.path.join(TEMPLATE_DIR, template_name)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    for key, value in context.items():
        placeholder = "{{ " + key + " }}"
        content = content.replace(placeholder, str(value))

    return content


def parse_post_body(handler):
    content_len = int(handler.headers.get("Content-Length", "0"))
    content_type = handler.headers.get("Content-Type", "")
    raw = handler.rfile.read(content_len).decode("utf-8") if content_len > 0 else ""
    if "application/x-www-form-urlencoded" in content_type:
        parsed = parse_qs(raw)
        return {k: v[0] if v else "" for k, v in parsed.items()}
    return {}

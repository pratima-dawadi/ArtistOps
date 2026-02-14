import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from src.controllers.auth import AuthController
from src.utils.template import render_template, parse_post_body

auth_controller = AuthController()


class AMSRequestHandler(BaseHTTPRequestHandler):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/static/style.css":
            css_path = os.path.join(self.BASE_DIR, "static", "style.css")

            if not os.path.exists(css_path):
                return self.not_found()
            with open(css_path, "r", encoding="utf-8") as f:
                css = f.read()

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/css; charset=utf-8")
            self.end_headers()
            self.wfile.write(css.encode("utf-8"))
            return

        if path == "/login":
            html = render_template("login.html")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        if path == "/register":
            html = render_template("register.html")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Welcome to ArtistOps!")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        form = parse_post_body(self)

        if path == "/register":
            success, result = auth_controller.register_user(form)

            if not success:
                self.send_response(302)
                self.send_header("Location", "/register")
                self.end_headers()
                self.wfile.write(
                    f"<h3>Login Error: {result}</h3><a href='/login'>Try again</a>".encode()
                )
                return

            self.send_response(302)
            self.send_header("Location", "/login")
            self.end_headers()
            return

        if path == "/login":
            success, result = auth_controller.login_user(form)

            if not success:
                self.send_response(HTTPStatus.UNAUTHORIZED)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    f"<h3>Login Error: {result}</h3><a href='/login'>Try again</a>".encode()
                )
                return

            self.send_response(302)
            self.send_header("Location", "/dashboard")
            self.end_headers()
            return

import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from src.controllers.artist import ArtistController
from src.controllers.auth import AuthController
from src.controllers.song import SongController
from src.controllers.user import UserController
from src.utils.session import (
    SESSION_COOKIE_NAME,
    create_session,
    destroy_session,
    get_session_id,
    get_user_from_session,
    require_login,
)
from src.utils.template import parse_post_body, render_template

artist_controller = ArtistController()
auth_controller = AuthController()
song_controller = SongController()
user_controller = UserController()


class AMSRequestHandler(BaseHTTPRequestHandler):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def send_html(self, html_text, status=HTTPStatus.OK):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html_text.encode("utf-8"))

    def redirect(self, target):
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", target)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        user = get_user_from_session(self)

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

        if path == "/":
            if user:
                return self.redirect("/dashboard")
            return self.redirect("/login")

        if path == "/login":
            if user:
                return self.redirect("/dashboard")
            return self.send_html(render_template("login.html"))

        if path == "/register":
            if user:
                return self.redirect("/dashboard")
            return self.send_html(render_template("register.html"))

        if path == "/dashboard":
            if not require_login(self):
                return
            tab = qs.get("tab", ["users"])[0]

            if tab == "users":
                users = user_controller.list_users()
                rows = ""
                for index, u in enumerate(users, start=1):
                    rows += f"""
                    <tr>
                    <form method="post" action="/users/update" style="display: inline;>
                        <input type="hidden" name="id" value="{u['id']}">
                        <td>{index}</td>
                        <td><input type="text" class="table-input" value="{u['first_name']}" name="first_name"></td>
                        <td><input type="text" class="table-input" value="{u['last_name']}" name="last_name"></td>
                        <td><input type="text" class="table-input" value="{u['email']}" name="email"></td>
                        <td><input type="text" class="table-input" value="{u['phone']}" name="phone"></td>
                        <td><input type="date" class="table-input" value="{u['dob']}" name="dob"></td>
                        <td>
                            <select class="table-select" name="gender">
                                <option value="m" {'selected' if u['gender'] == 'm' else ''}>m</option>
                                <option value="f" {'selected' if u['gender'] == 'f' else ''}>f</option>
                                <option value="o" {'selected' if u['gender'] == 'o' else ''}>o</option>
                            </select>
                        </td>
                        <td><input type="text" class="table-input" value="{u['address']}" name="address"></td>
                        <td>
                            <select class="table-select" name="role">
                                <option value="super_admin" {'selected' if u['role'] == 'super_admin' else ''}>super_admin</option>
                                <option value="artist_manager" {'selected' if u['role'] == 'artist_manager' else ''}>artist_manager</option>
                                <option value="artist" {'selected' if u['role'] == 'artist' else ''}>artist</option>
                            </select>
                        </td>
                        <td>
                                <input type='hidden' name='id' value='{u['id']}'>
                                <button type="submit" class="btn btn-update">Update</button>
                        </td>
                    </form>
                        <td>
                            <form method='post' action='/users/delete' style="display: inline;">
                                <input type='hidden' name='id' value='{u['id']}'>
                                <button type="submit" class="btn btn-delete">Delete</button>
                            </form>
                        </td>
                    </tr>
                    """

                table = render_template("users_table.html", rows=rows)
                content = render_template("dashboard.html", table=table)
                page = render_template(
                    "base.html",
                    title="Dashboard",
                    content=content,
                    users_active="active",
                    artists_active="",
                )
                self.send_html(page)
                return

            elif tab == "artists":
                artists = artist_controller.list_artists()
                rows = ""
                for index, a in enumerate(artists, start=1):
                    artist_id = a["id"]
                    rows += f"""
                    <tr>
                        <form method='post' action='/artists/update' style="display: inline;">
                            <input type="hidden" name="id" value="{a['id']}">

                            <td>{index}</td>
                            <td><input type="text" class="table-input" value="{a['stage_name']}" name="stage_name"></td>
                            <td><input type="number" class="table-input" value="{a['first_release_year']}" name="first_release_year"></td>
                            <td><input type="number" class="table-input" value="{a['no_of_albums_released']}" name="no_of_albums_released"></td>
                            <td>
                                <button class="btn btn-update">
                                    <a href="/artists/{artist_id}/songs" style="color:white">Songs</a>
                                </button>
                            </td>
                            <td>
                                <input type='hidden' name='id' value='{a['id']}'>
                                <button type="submit" class="btn btn-update">Update</button>
                            </td>
                        </form>
                        <td>
                        
                            <div class="action-cell">
                                <form method='post' action='/artists/delete' style="display: inline;">
                                    <input type='hidden' name='id' value='{a['id']}'>
                                    <button type="submit" class="btn btn-delete">Delete</button>
                                </form>
                            </div>
                        </td>
                    </tr>
                    """

                table = render_template("artists_table.html", rows=rows)
                content = render_template("dashboard.html", table=table)
                page = render_template(
                    "base.html",
                    title="Dashboard",
                    content=content,
                    users_active="",
                    artists_active="active",
                )
                self.send_html(page)
                return

        if path.startswith("/artists/") and path.endswith("/songs"):
            if not require_login(self):
                return
            artist_id = path.split("/")[2]

            artist = artist_controller.get_artist_by_id(artist_id)
            if not artist:
                self.send_error(HTTPStatus.NOT_FOUND, "Artist not found")
                return

            artist_name = artist["stage_name"]

            songs = song_controller.list_artist_song(artist_id)

            rows = ""
            if songs:
                for index, s in enumerate(songs, start=1):
                    rows += f"""
                        <tr>
                            <form method="post" action="/songs/update">
                                <td>{index}</td>

                                <td>
                                    <input type="text" name="title" value="{s['title']}" class="table-input">
                                </td>

                                <td>
                                    <input type="text" name="album_name" value="{s['album_name']}" class="table-input">
                                </td>

                                <td>
                                    <select name="genre" class="table-input">
                                        <option value="rnb" {"selected" if s['genre']=="rnb" else ""}>rnb</option>
                                        <option value="country" {"selected" if s['genre']=="country" else ""}>country</option>
                                        <option value="classic" {"selected" if s['genre']=="classic" else ""}>classic</option>
                                        <option value="rock" {"selected" if s['genre']=="rock" else ""}>rock</option>
                                        <option value="jazz" {"selected" if s['genre']=="jazz" else ""}>jazz</option>
                                    </select>
                                </td>

                                <td>
                                    <input type="hidden" name="id" value="{s['id']}">
                                    <input type="hidden" name="artist_id" value="{artist_id}">
                                    <button type="submit" class="btn btn-update">Update</button>
                                </td>
                            </form>

                            <td>
                                <form method="post" action="/songs/delete">
                                    <input type="hidden" name="id" value="{s['id']}">
                                    <input type="hidden" name="artist_id" value="{artist_id}">
                                    <button type="submit" class="btn btn-delete">Delete</button>
                                </form>
                            </td>
                        </tr>
                        """
            else:
                rows = """
                <tr>
                    <td colspan="6" style="text-align: center; padding: 2rem; color: #999;">
                        No songs found for this artist
                    </td>
                </tr>
                """

            content = render_template(
                "songs_table.html",
                rows=rows,
                artist_name=artist_name,
                artist_id=artist_id,
            )
            page = render_template(
                "base.html",
                title=f"Songs - {artist_name}",
                content=content,
                users_active="",
                artists_active="active",
            )
            self.send_html(page)
            return

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        form = parse_post_body(self)
        user = get_user_from_session(self)

        if path == "/register":
            if user:
                return self.redirect("/dashboard")
            success, result = auth_controller.register_user(form)
            if not success:
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header("Location", "/register")
                self.end_headers()
                return
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", "/login")
            self.end_headers()
            return

        if path == "/login":
            if user:
                return self.redirect("/dashboard")
            success, result = auth_controller.login_user(form)

            if not success:
                self.send_response(HTTPStatus.UNAUTHORIZED)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    f"<h3>Login Error: {result}</h3><a href='/login'>Try again</a>".encode()
                )
                return

            session_id = create_session(result)
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", "/dashboard")
            self.send_header(
                "Set-Cookie",
                f"{SESSION_COOKIE_NAME}={session_id}; Path=/; HttpOnly; SameSite=Lax",
            )
            self.end_headers()
            return

        if path == "/logout":
            session_id = get_session_id(self)
            destroy_session(session_id)
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", "/login")
            self.send_header(
                "Set-Cookie",
                f"{SESSION_COOKIE_NAME}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax",
            )
            self.end_headers()
            return

        if not require_login(self):
            return

        if path == "/users/create":
            if not require_login(self):
                return
            user_controller.create_user(form)
            return self.redirect("/dashboard?tab=users")

        if path == "/users/delete":
            if not require_login(self):
                return
            user_controller.delete_user(form["id"])
            return self.redirect("/dashboard?tab=users")

        if path == "/users/update":
            if not require_login(self):
                return
            user_controller.update_user(form)
            return self.redirect("/dashboard?tab=users")

        if path == "/artists/create":
            if not require_login(self):
                return
            artist_controller.create_artist(form)
            return self.redirect("/dashboard?tab=artists")

        if path == "/artists/update":
            if not require_login(self):
                return
            artist_controller.update_artist(form)
            return self.redirect("/dashboard?tab=artists")

        if path == "/artists/delete":
            if not require_login(self):
                return
            artist_controller.delete_artist(form["id"])
            return self.redirect("/dashboard?tab=artists")

        if path == "/songs/create":
            if not require_login(self):
                return
            required_fields = ["artist_id", "title", "album_name", "genre"]

            for field in required_fields:
                if not form.get(field):
                    return self.redirect("/dashboard?tab=artists")

            try:
                song_controller.create_song(form)
            except Exception:
                return self.redirect("/dashboard?tab=artists")

            artist_id = form.get("artist_id")
            return self.redirect(f"/artists/{artist_id}/songs")

        if path == "/songs/update":
            if not require_login(self):
                return
            song_controller.update_song(form)
            return self.redirect(f"/artists/{form['artist_id']}/songs")

        if path == "/songs/delete":
            if not require_login(self):
                return
            song_controller.delete_song(form["id"])
            return self.redirect(f"/artists/{form['artist_id']}/songs")

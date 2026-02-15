import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from src.controllers.artist import ArtistController
from src.controllers.auth import AuthController
from src.controllers.song import SongController
from src.controllers.user import UserController
from src.utils.enums import Role
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

PAGE_SIZE = 2


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

    def forbidden(self, message="Forbidden"):
        self.send_html(f"<h3>{message}</h3>", status=HTTPStatus.FORBIDDEN)

    def get_page(self, qs):
        raw_page = qs.get("page", ["1"])[0]
        try:
            page = int(raw_page)
        except ValueError:
            return 1
        return max(1, page)

    def build_pagination(self, base_path, page, total_count):
        total_pages = max(1, (total_count + PAGE_SIZE - 1) // PAGE_SIZE)
        prev_page = max(1, page - 1)
        next_page = min(total_pages, page + 1)
        prev_disabled = "disabled" if page <= 1 else ""
        next_disabled = "disabled" if page >= total_pages else ""

        return f"""
        <div class="pagination">
            <a class="page-btn {prev_disabled}" href="{base_path}&page={prev_page}">Previous</a>
            <span class="page-meta">Page {page} of {total_pages}</span>
            <a class="page-btn {next_disabled}" href="{base_path}&page={next_page}">Next</a>
        </div>
        """

    def has_role(self, user, *roles):
        if not user:
            return False
        return user.get("role") in roles

    def can_access_artist_songs(self, user, artist_id):
        role = user.get("role")
        if role in (Role.SUPER_ADMIN.value, Role.ARTIST_MANAGER.value):
            return True
        if role == Role.ARTIST.value:
            artist = artist_controller.get_artist_by_user_id(user.get("id"))
            return bool(artist and str(artist["id"]) == str(artist_id))
        return False

    def render_base(self, user, content, users_active="", artists_active=""):
        role = user.get("role")

        users_tab = ""
        artists_tab = ""

        if role == Role.SUPER_ADMIN.value:
            users_tab = f'<a href="/dashboard?tab=users" class="nav-tab {users_active}">Users</a>'
            artists_tab = f'<a href="/dashboard?tab=artists" class="nav-tab {artists_active}">Artists</a>'
        elif role == Role.ARTIST_MANAGER.value:
            artists_tab = f'<a href="/dashboard?tab=artists" class="nav-tab {artists_active}">Artists</a>'

        full_name = f"{user.get('first_name','')} {user.get('last_name','')}".strip()
        full_role = Role(role).name if role in Role._value2member_map_ else role

        user_info = f"{full_name} ({full_role})"

        return render_template(
            "base.html",
            title="Dashboard",
            content=content,
            users_tab=users_tab,
            artists_tab=artists_tab,
            user_info=user_info,
        )

    def render_users_tab(self, user, page):
        if not self.has_role(user, Role.SUPER_ADMIN.value):
            return self.forbidden("Only super_admin can access users tab.")

        users, total_count = user_controller.list_users(page=page, page_size=PAGE_SIZE)

        rows = ""
        for index, u in enumerate(users, start=((page - 1) * PAGE_SIZE) + 1):
            rows += f"""
            <tr>
                <form method="post" action="/users/update" style="display: inline;">
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

        create_form = """
        <div class="content-section">
            <h2 class="section-title">Create User</h2>
            <form method="post" action="/users/create" class="create-user-form">
                <div class="form-grid">
                    <div class="form-group"><input type="text" name="first_name" class="form-input" placeholder="first_name" required></div>
                    <div class="form-group"><input type="text" name="last_name" class="form-input" placeholder="last_name" required></div>
                    <div class="form-group"><input type="email" name="email" class="form-input" placeholder="email" required></div>
                    <div class="form-group"><input type="password" name="password" class="form-input" placeholder="password" required></div>
                    <div class="form-group"><input type="text" name="phone" class="form-input" placeholder="phone" required></div>
                </div>
                <div class="form-grid">
                    <div class="form-group"><input type="date" name="dob" class="form-input" required></div>
                    <div class="form-group">
                        <select name="gender" class="form-select" required>
                            <option value="m">m</option>
                            <option value="f">f</option>
                            <option value="o">o</option>
                        </select>
                    </div>
                    <div class="form-group"><input type="text" name="address" class="form-input" placeholder="address" required></div>
                    <div class="form-group">
                        <select name="role" id="roleSelect" class="form-select" required>
                            <option value="super_admin">super_admin</option>
                            <option value="artist_manager">artist_manager</option>
                            <option value="artist">artist</option>
                        </select>
                    </div>
                </div>
                <div class="form-grid">
                    <div class="form-group" id="artistFields" style="display:none; margin-top:10px;">
                        <input type="text" name="stage_name" placeholder="Stage Name">
                        <input type="number" name="first_release_year" placeholder="First Release Year">
                        <input type="number" name="no_of_albums_released" placeholder="No. of Albums Released">
                    </div>
                </div>
                <button type="submit" class="submit-btn">Create</button>
            </form>
        </div>
        """
        pagination = self.build_pagination("/dashboard?tab=users", page, total_count)

        table = render_template(
            "users_table.html",
            rows=rows,
            create_form=create_form,
            pagination=pagination,
        )
        content = render_template("dashboard.html", table=table)
        page_html = self.render_base(user, content, users_active="active")
        return self.send_html(page_html)

    def render_artists_tab(self, user, page):
        if not self.has_role(user, Role.SUPER_ADMIN.value, Role.ARTIST_MANAGER.value):
            return self.forbidden(
                "Only super_admin and artist_manager can access artists tab."
            )

        artists, total_count = artist_controller.list_artists(
            page=page, page_size=PAGE_SIZE
        )
        is_manager = user.get("role") == Role.ARTIST_MANAGER.value

        rows = ""
        for index, a in enumerate(artists, start=((page - 1) * PAGE_SIZE) + 1):
            artist_id = a["id"]
            if is_manager:
                rows += f"""
                <tr>
                    <form method='post' action='/artists/update' style="display: inline;">
                        <input type="hidden" name="id" value="{a['id']}">
                        <td>{index}</td>
                        <td><input type="text" class="table-input" value="{a['stage_name']}" name="stage_name"></td>
                        <td><input type="number" class="table-input" value="{a['first_release_year']}" name="first_release_year"></td>
                        <td><input type="number" class="table-input" value="{a['no_of_albums_released']}" name="no_of_albums_released"></td>
                        <td><a class="btn btn-update songs-link" href="/artists/{artist_id}/songs">Songs</a></td>
                        <td><button type="submit" class="btn btn-update">Update</button></td>
                    </form>
                    <td>
                        <form method='post' action='/artists/delete' style="display: inline;">
                            <input type='hidden' name='id' value='{a['id']}'>
                            <button type="submit" class="btn btn-delete">Delete</button>
                        </form>
                    </td>
                </tr>
                """
            else:
                rows += f"""
                <tr>
                    <td>{index}</td>
                    <td>{a['stage_name']}</td>
                    <td>{a['first_release_year']}</td>
                    <td>{a['no_of_albums_released']}</td>
                    <td><a class="btn btn-update songs-link" href="/artists/{artist_id}/songs">Songs</a></td>
                    <td><button type="button" class="btn btn-update" disabled>Update</button></td>
                    <td><button type="button" class="btn btn-delete" disabled>Delete</button></td>
                </tr>
                """

        create_form = ""
        if is_manager:
            create_form = """
            <div class="content-section">
                <h2 class="section-title">Create Artist</h2>
                <form method="post" action="/artists/create" class="create-user-form">
                    <div class="form-grid">
                        <div class="form-group"><input type="text" name="first_name" class="form-input" placeholder="first_name" required></div>
                        <div class="form-group"><input type="text" name="last_name" class="form-input" placeholder="last_name" required></div>
                        <div class="form-group"><input type="email" name="email" class="form-input" placeholder="email" required></div>
                        <div class="form-group"><input type="password" name="password" class="form-input" placeholder="password" required></div>
                        <div class="form-group"><input type="text" name="phone" class="form-input" placeholder="phone" required></div>
                    </div>
                    <div class="form-grid">
                        <div class="form-group"><input type="date" name="dob" class="form-input" required></div>
                        <div class="form-group">
                            <select name="gender" class="form-select" required>
                                <option value="m">m</option>
                                <option value="f">f</option>
                                <option value="o">o</option>
                            </select>
                        </div>
                        <div class="form-group"><input type="text" name="address" class="form-input" placeholder="address" required></div>
                        <div class="form-group"><input type="text" name="stage_name" class="form-input" placeholder="stage_name" required></div>
                        <div class="form-group"><input type="number" name="first_release_year" class="form-input" placeholder="first_release_year" required></div>
                        <div class="form-group"><input type="number" name="no_of_albums_released" class="form-input" placeholder="no_of_albums_released" required></div>
                    </div>
                    <button type="submit" class="submit-btn">Create Artist</button>
                </form>
            </div>
            """
        pagination = self.build_pagination("/dashboard?tab=artists", page, total_count)
        table = render_template(
            "artists_table.html",
            rows=rows,
            create_form=create_form,
            pagination=pagination,
        )
        content = render_template("dashboard.html", table=table)
        page_html = self.render_base(user, content, artists_active="active")
        return self.send_html(page_html)

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

            role = user.get("role")

            if role == Role.ARTIST.value:
                own_artist = artist_controller.get_artist_by_user_id(user.get("id"))
                if not own_artist:
                    return self.forbidden("Artist profile not found for current user.")
                return self.redirect(f"/artists/{own_artist['id']}/songs")

            default_tab = "users" if role == Role.SUPER_ADMIN.value else "artists"
            tab = qs.get("tab", [default_tab])[0]
            page = self.get_page(qs)

            if tab == "users":
                return self.render_users_tab(user, page)
            if tab == "artists":
                return self.render_artists_tab(user, page)

            return self.redirect("/dashboard")

        if path.startswith("/artists/") and path.endswith("/songs"):
            if not require_login(self):
                return
            artist_id = path.split("/")[2]

            if not self.can_access_artist_songs(user, artist_id):
                return self.forbidden("You do not have access to this artist's songs.")

            artist = artist_controller.get_artist_by_id(artist_id)
            if not artist:
                self.send_error(HTTPStatus.NOT_FOUND, "Artist not found")
                return

            artist_name = artist["stage_name"]

            songs = song_controller.list_artist_song(artist_id)

            can_mutate_songs = user.get(
                "role"
            ) == Role.ARTIST.value and self.can_access_artist_songs(user, artist_id)

            rows = ""
            if songs:
                for index, s in enumerate(songs, start=1):
                    if can_mutate_songs:
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
                        rows += f"""
                        <tr>
                            <td>{index}</td>
                            <td>{s['title']}</td>
                            <td>{s['album_name']}</td>
                            <td>{s['genre']}</td>
                            <td><button type="button" class="btn btn-update" disabled>Update</button></td>
                            <td><button type="button" class="btn btn-delete" disabled>Delete</button></td>
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

            create_song_form = ""
            if can_mutate_songs:
                create_song_form = f"""
                <div class="content-section">
                    <h2 class="section-title">Create Song for Artist: {artist_name}</h2>
                    <form method="post" action="/songs/create" class="create-user-form">
                        <input type="hidden" name="artist_id" value="{artist_id}">
                        <div class="form-grid">
                            <div class="form-group"><input type="text" name="title" class="form-input" placeholder="title" required></div>
                            <div class="form-group"><input type="text" name="album_name" class="form-input" placeholder="album_name" required></div>
                            <div class="form-group">
                                <select name="genre" class="form-select" required>
                                    <option value="">Select Genre</option>
                                    <option value="rnb">rnb</option>
                                    <option value="country">country</option>
                                    <option value="classic">classic</option>
                                    <option value="rock">rock</option>
                                    <option value="jazz">jazz</option>
                                </select>
                            </div>
                        </div>
                        <button type="submit" class="submit-btn">Create Song</button>
                    </form>
                </div>
                """

            content = render_template(
                "songs_table.html",
                rows=rows,
                artist_name=artist_name,
                artist_id=artist_id,
                create_song_form=create_song_form,
            )
            html_page = self.render_base(user, content, artists_active="active")

            self.send_html(html_page)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")
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
                self.send_response(HTTPStatus.BAD_REQUEST)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    f"<h3>Registration Error: {result}</h3><a href='/register'>Try again</a>".encode()
                )
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
            if not self.has_role(user, Role.SUPER_ADMIN.value):
                return self.forbidden("Only super_admin can create users.")
            user_controller.create_user(form)
            return self.redirect("/dashboard?tab=users")

        if path == "/users/delete":
            if not self.has_role(user, Role.SUPER_ADMIN.value):
                return self.forbidden("Only super_admin can delete users.")
            user_controller.delete_user(form["id"])
            return self.redirect("/dashboard?tab=users")

        if path == "/users/update":
            if not self.has_role(user, Role.SUPER_ADMIN.value):
                return self.forbidden("Only super_admin can update users.")
            user_controller.update_user(form)
            return self.redirect("/dashboard?tab=users")

        if path == "/artists/create":
            if not self.has_role(user, Role.ARTIST_MANAGER.value):
                return self.forbidden("Only artist_manager can create artists.")
            artist_controller.create_artist(form)
            return self.redirect("/dashboard?tab=artists")

        if path == "/artists/update":
            if not self.has_role(user, Role.ARTIST_MANAGER.value):
                return self.forbidden("Only artist_manager can update artists.")
            artist_controller.update_artist(form)
            return self.redirect("/dashboard?tab=artists")

        if path == "/artists/delete":
            if not self.has_role(user, Role.ARTIST_MANAGER.value):
                return self.forbidden("Only artist_manager can delete artists.")
            artist_controller.delete_artist(form["id"])
            return self.redirect("/dashboard?tab=artists")

        if path == "/songs/create":
            artist_id = form.get("artist_id")

            if not artist_id or not self.has_role(user, Role.ARTIST.value):
                return self.forbidden("Only artist can create songs.")

            if not self.can_access_artist_songs(user, artist_id):
                return self.forbidden(
                    "You can only create songs for your own artist profile."
                )

            required_fields = ["artist_id", "title", "album_name", "genre"]

            for field in required_fields:
                if not form.get(field):
                    return self.redirect(f"/artists/{artist_id}/songs")

            song_controller.create_song(form)
            return self.redirect(f"/artists/{artist_id}/songs")

        if path == "/songs/update":
            if not self.has_role(user, Role.ARTIST.value):
                return self.forbidden("Only artist can update songs.")

            song = song_controller.get_song_by_id(form.get("id"))
            if not song or not self.can_access_artist_songs(user, song["artist_id"]):
                return self.forbidden(
                    "You can only update songs for your own artist profile."
                )

            form["artist_id"] = str(song["artist_id"])
            song_controller.update_song(form)
            return self.redirect(f"/artists/{form['artist_id']}/songs")

        if path == "/songs/delete":
            if not self.has_role(user, Role.ARTIST.value):
                return self.forbidden("Only artist can delete songs.")

            song = song_controller.get_song_by_id(form.get("id"))
            if not song or not self.can_access_artist_songs(user, song["artist_id"]):
                return self.forbidden(
                    "You can only delete songs for your own artist profile."
                )

            artist_id = song["artist_id"]
            song_controller.delete_song(form["id"])
            return self.redirect(f"/artists/{artist_id}/songs")

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")
        return

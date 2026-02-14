from http.server import BaseHTTPRequestHandler


class AMSRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Welcome to ArtistOps!")

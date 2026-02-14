from http.server import ThreadingHTTPServer

from src.database.database import AMSDatabase
from src.server import AMSRequestHandler

PORT = 8000


def run_server():
    db = AMSDatabase()
    db.init_db()
    server_address = ("", PORT)
    server = ThreadingHTTPServer(server_address, AMSRequestHandler)
    print(f"Application is running at http://localhost:{PORT}/login")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
    print("Server stopped.")


if __name__ == "__main__":
    run_server()

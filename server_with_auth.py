# Geomap: helyi szerver jelszavas megtekintessel (HTTP Basic Auth).
# A .env fajlbol olvassa a WEB_AUTH_USER es WEB_AUTH_HASH ertekeket.
# Nagy .json fajlok gzip-pel mennek (gyorsabb betoltes).

import os
import base64
import gzip
import hashlib
import io
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080
ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(ROOT, ".env")

def load_env():
    env = {}
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env

def check_auth(env, username, password):
    user = env.get("WEB_AUTH_USER", "").strip()
    want_hash = env.get("WEB_AUTH_HASH", "").strip().lower()
    if not user or not want_hash:
        return False
    if username != user:
        return False
    h = hashlib.sha256(password.encode("utf-8")).hexdigest().lower()
    return h == want_hash

class AuthHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        env = load_env()
        user_ok = env.get("WEB_AUTH_USER") and env.get("WEB_AUTH_HASH")
        if not user_ok:
            self.send_error(503, "Eloszor futtasd: scripts\\setup-web-auth.ps1  (WEB_AUTH_USER es WEB_AUTH_HASH a .env-ben)")
            return
        auth = self.headers.get("Authorization")
        if not auth or not auth.startswith("Basic "):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Geomap"')
            self.end_headers()
            self.wfile.write(b"Jelszo szukseges.")
            return
        try:
            raw = base64.b64decode(auth[6:].strip()).decode("utf-8")
            username, _, password = raw.partition(":")
        except Exception:
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Geomap"')
            self.end_headers()
            return
        if not check_auth(env, username, password):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Geomap"')
            self.end_headers()
            self.wfile.write(b"Hibas felhasznalonev vagy jelszo.")
            return
        if self.path in ("/", "", "/index.html"):
            self.send_response(302)
            self.send_header("Location", "/heatmap.html")
            self.end_headers()
            return
        path = self.translate_path(self.path)
        if os.path.isfile(path) and path.lower().endswith(".json") and "gzip" in (self.headers.get("Accept-Encoding") or "").lower():
            try:
                with open(path, "rb") as f:
                    data = f.read()
                buf = io.BytesIO()
                with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
                    gz.write(data)
                body = buf.getvalue()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Encoding", "gzip")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            except Exception:
                pass
        super().do_GET()

    def log_message(self, format, *args):
        print(format % args)

def main():
    os.chdir(ROOT)
    server = HTTPServer(("", PORT), AuthHandler)
    print("Geomap szerver (jelszavas): http://127.0.0.1:%s/" % PORT)
    print("Megtekinteshez add meg a .env-ben beallitott felhasznalot es jelszot.")
    server.serve_forever()

if __name__ == "__main__":
    main()

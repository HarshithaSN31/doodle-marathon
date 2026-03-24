import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import mimetypes

PORT = int(os.environ.get('PORT', 8085))
DB_FILE = "doodles_db.json"

print(f"Loading database from {DB_FILE}...")
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        try:
            doodles = json.load(f)
        except:
            doodles = []
else:
    doodles = []

class MultiplayerHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        path = self.path.split('?')[0].rstrip('/')
        print(f"LOG: GET {path}")
        
        if path == '/api/doodles':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(doodles).encode())
        else:
            # Serve static files manually
            fpath = self.path.split('?')[0]
            if fpath == '/': fpath = '/index.html'
            fpath = '.' + fpath
            
            if os.path.exists(fpath) and os.path.isfile(fpath):
                self.send_response(200)
                ctype, _ = mimetypes.guess_type(fpath)
                self.send_header('Content-Type', ctype or 'text/plain')
                self._send_cors_headers()
                self.end_headers()
                with open(fpath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Not Found")

    def do_POST(self):
        global doodles
        path = self.path.split('?')[0].rstrip('/')
        print(f"LOG: POST {path}")
        
        if path == '/api/doodles':
            length = int(self.headers['Content-Length'])
            data = self.rfile.read(length)
            try:
                new_doodle = json.loads(data.decode('utf-8'))
                doodles.append(new_doodle)
                with open(DB_FILE, "w") as f:
                    json.dump(doodles, f)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(b'{"success": true}')
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(str(e).encode())
                
        elif path == '/api/delete':
            length = int(self.headers['Content-Length'])
            data = self.rfile.read(length)
            try:
                req = json.loads(data.decode('utf-8'))
                idx = req.get('index')
                client_id = req.get('clientId')
                if idx is not None and 0 <= idx < len(doodles):
                    if doodles[idx].get('clientId') == client_id or not doodles[idx].get('clientId'):
                        doodles.pop(idx)
                        with open(DB_FILE, "w") as f:
                            json.dump(doodles, f)
                        self.send_response(200)
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(b'{"success": true}')
                    else:
                        self.send_response(403)
                        self.end_headers()
                else:
                    self.send_response(400)
                    self.end_headers()
            except:
                self.send_response(400)
                self.end_headers()

    def log_message(self, format, *args):
        # Suppress default HTTP logging; we use our own LOG: prefix above
        pass

if __name__ == '__main__':
    # Listen on '0.0.0.0' for Render to be able to reach the service
    httpd = HTTPServer(('0.0.0.0', PORT), MultiplayerHandler)
    print(f"Doodle Marathon Data Engine running on port {PORT}")
    print("Press Ctrl+C to stop.")
    httpd.serve_forever()


import http.server
import socketserver
import mimetypes
import sys
import os
import urllib.parse

PORT = 8080

mimetypes.add_type('application/wasm', '.wasm')
mimetypes.add_type('model/gltf-binary', '.glb')
mimetypes.add_type('model/gltf+json', '.gltf')
mimetypes.add_type('image/ktx2', '.ktx2')
mimetypes.add_type('image/avif', '.avif')
mimetypes.add_type('image/webp', '.webp')
mimetypes.add_type('video/webm', '.webm')
mimetypes.add_type('font/woff2', '.woff2')

class CleanURLHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.end_headers()

    def translate_path(self, path):
        # Base translation from SimpleHTTPRequestHandler
        clean_path = path.split('?', 1)[0].split('#', 1)[0]
        unquoted = urllib.parse.unquote(clean_path)
        
        # Default root translation
        translated = super().translate_path(unquoted)
        
        # If the direct path exists, use it
        if os.path.exists(translated):
            if os.path.isdir(translated):
                index_candidate = os.path.join(translated, 'index.html')
                if os.path.exists(index_candidate):
                    return index_candidate
            return translated

        # Check path + '.html' for clean URLs (e.g., /products -> products.html)
        if os.path.exists(translated + '.html'):
            return translated + '.html'

        # Check path / 'index.html'
        index_in_dir = os.path.join(translated, 'index.html')
        if os.path.exists(index_in_dir):
            return index_in_dir

        # Fallback for /favicon.ico
        if clean_path in ['/favicon.ico', 'favicon.ico']:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            fav = os.path.join(base_dir, 'favicon.ico')
            if os.path.exists(fav):
                return fav

        return translated

    def log_message(self, format, *args):
        # Ignore client aborts and keep log clean
        try:
            super().log_message(format, *args)
        except Exception:
            pass

class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    with ThreadingServer(("", port), CleanURLHandler) as httpd:
        print(f"Dialed Coffee threaded web server running at http://localhost:{port}/", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.", flush=True)

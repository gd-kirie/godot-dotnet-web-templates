"""Serve a local Web export with the required cross-origin isolation headers."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import sys


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=sys.argv[1], **kwargs)

    def end_headers(self):
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        super().end_headers()


ThreadingHTTPServer(('127.0.0.1', 8765), Handler).serve_forever()

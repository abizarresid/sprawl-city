#!/usr/bin/env python3
"""Serve the game on http://localhost:8123 with caching turned off, so the browser always loads the newest build."""
import http.server, socketserver

class NoCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Expires', '0')
        super().end_headers()

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(('', 8123), NoCache) as httpd:
    print('Sprawl City on http://localhost:8123  (Ctrl+C to stop)')
    httpd.serve_forever()

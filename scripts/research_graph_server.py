#!/usr/bin/env python3
"""Serve a read-only dashboard without restarting the active queue process.

This process has no controller, worker imports, or mutation route.
It reads the existing authenticated API. The mutation token stays server-side.
"""
import json
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from research_graph_view import render_graph
from workflow_metadata439 import enrich

ROOT = Path(__file__).resolve().parent.parent


class Snapshot:
    def __init__(self):
        self.lock = threading.Lock()
        self.value = None
        self.updated = 0

    def read(self):
        with self.lock:
            if self.value is not None and time.monotonic()-self.updated < 10:
                return self.value
            control = json.loads((ROOT/'.build/dashboard/control.json').read_text())
            # Do not follow an arbitrary URL from a modified local control file.
            origin = 'http://127.0.0.1:8765'
            if control['origin'] != origin:
                raise ValueError('Unexpected queue origin')
            request = urllib.request.Request(origin+'/api/state', headers={
                'Authorization':'Bearer '+control['token'], 'Origin':origin})
            with urllib.request.urlopen(request, timeout=45) as response:
                raw = response.read(32*1024*1024+1)
            if len(raw) > 32*1024*1024:
                raise ValueError('Snapshot exceeds 32 MiB')
            value = json.loads(raw)
            if not isinstance(value.get('jobs'), list):
                raise ValueError('Snapshot lacks jobs')
            value = enrich(value, ROOT/'reports/work/research-queue')
            value['graphCompanion'] = True
            self.value, self.updated = value, time.monotonic()
            return value


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, body, kind='application/json'):
        payload = (json.dumps(body) if kind=='application/json' else body).encode()
        self.send_response(code)
        self.send_header('Content-Type', kind+'; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(payload)

    def valid(self):
        origins = [f'http://{host}:8766' for host in ('127.0.0.1','localhost')]
        return ('http://'+self.headers.get('Host','') in origins and
                (not self.headers.get('Origin') or self.headers['Origin'] in origins))

    def do_GET(self):
        if not self.valid():
            return self.reply(403, {'error':'request_refused'})
        if self.path not in ('/', '/api/state'):
            return self.reply(404, {'error':'not_found'})
        try:
            value = self.server.snapshot.read()
            return self.reply(200, render_graph(value), 'text/html') if self.path=='/' else self.reply(200, value)
        except Exception:
            # Never put a private token, local path, or upstream response into an error.
            return self.reply(503, {'error':'Queue snapshot unavailable. The experiment runner is unchanged.'})

    def do_POST(self):
        self.reply(405, {'error':'read_only'})

    def log_message(self, *_):
        pass


def main():
    server = ThreadingHTTPServer(('127.0.0.1',8766),Handler)
    server.snapshot = Snapshot()
    server.serve_forever()


if __name__ == '__main__':
    main()

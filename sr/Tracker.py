# tracker.py
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# Tracker storage for peers and files
peers = {}
files = {}

class TrackerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/announce":
            self.handle_announce()

    def handle_announce(self):
        # Parse parameters from URL
        query = self.path.split('?')[-1]
        params = dict(qc.split("=") for qc in query.split("&"))
        peer_id = params['peer_id']
        file_hash = params['file_hash']
        ip = self.client_address[0]
        port = int(params['port'])
        
        # Update peer info in tracker
        if file_hash not in files:
            files[file_hash] = []
        files[file_hash].append({'peer_id': peer_id, 'ip': ip, 'port': port})

        # Response with peer list for this file
        peer_list = [p for p in files[file_hash] if p['peer_id'] != peer_id]
        response = {'peers': peer_list}
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run_tracker(host="0.0.0.0", port=8080):
    server = HTTPServer((host, port), TrackerHandler)
    print(f"Tracker is running on {host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run_tracker()

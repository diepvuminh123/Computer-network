# node.py
import socket
import threading
import requests
import json
import os

TRACKER_HOST = 'localhost'
TRACKER_PORT = 8080
PEER_ID = f"peer_{socket.gethostname()}"

def announce_to_tracker(file_hash, port):
    # Announce to tracker with the file hash and port
    url = f"http://{TRACKER_HOST}:{TRACKER_PORT}/announce"
    params = {
        'peer_id': PEER_ID,
        'file_hash': file_hash,
        'port': port
    }
    response = requests.get(url, params=params)
    peers = response.json().get('peers', [])
    print(f"Peers for file {file_hash}: {peers}")
    return peers

def download_from_peer(ip, port, file_hash):
    # Connect to peer and download pieces of file
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))
            s.sendall(file_hash.encode('utf-8'))
            data = s.recv(1024)
            with open(file_hash, 'wb') as f:
                f.write(data)
            print(f"Downloaded file from {ip}:{port}")
    except Exception as e:
        print(f"Failed to download from {ip}:{port} - {e}")

def start_node(file_hash):
    # Start node as both client and server
    port = 9000
    peers = announce_to_tracker(file_hash, port)
    
    # Download from peers
    for peer in peers:
        threading.Thread(target=download_from_peer, args=(peer['ip'], peer['port'], file_hash)).start()

if __name__ == "__main__":
    file_hash = "sample_file_hash"  # Replace with actual file hash
    start_node(file_hash)

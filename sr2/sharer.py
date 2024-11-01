# server.py
import socket
import threading
import os

SHARED_DIR = "shared_files"
os.makedirs(SHARED_DIR, exist_ok=True)
PEER_PORT = 50001

def handle_download_request(conn, addr):
    try:
        data = conn.recv(1024).decode('utf-8')
        request = json.loads(data)
        if request["action"] == "download":
            file_name = request["file_name"]
            piece_index = request["piece_index"]
            part_path = os.path.join(SHARED_DIR, f"{file_name}_part_{piece_index}")

            if os.path.exists(part_path):
                with open(part_path, "rb") as f:
                    conn.sendall(f.read())
            else:
                conn.sendall(b"")  # Send empty if file part doesn't exist
    finally:
        conn.close()

def start_peer_server():
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_socket.bind(('localhost', PEER_PORT))
    peer_socket.listen()
    print(f"Peer server running on port {PEER_PORT}")

    while True:
        conn, addr = peer_socket.accept()
        threading.Thread(target=handle_download_request, args=(conn, addr)).start()

if __name__ == "__main__":
    start_peer_server()

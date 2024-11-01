import socket
import threading
import json

TRACKER_HOST = 'localhost'
TRACKER_PORT = 55555

# Store each piece with peer information
file_registry = {}

def register_piece(data, addr):
    file_name = data["file_name"]
    piece_index = data["piece_index"]
    peer_port = data["peer_port"]

    if file_name not in file_registry:
        file_registry[file_name] = {}
    if piece_index not in file_registry[file_name]:
        file_registry[file_name][piece_index] = []

    # Register IP address and port of the sharer
    file_registry[file_name][piece_index].append((addr[0], peer_port))

    return {"status": "registered", "file_name": file_name, "piece_index": piece_index}

def handle_client(conn, addr):
    try:
        data = conn.recv(1024).decode('utf-8')
        request = json.loads(data)
        action = request.get("action")

        if action == "register":
            response = register_piece(request, addr)
        elif action == "get_peers":
            file_name = request["file_name"]
            piece_index = request["piece_index"]
            response = {"peers": file_registry.get(file_name, {}).get(piece_index, [])}
        else:
            response = {"status": "unknown action"}

        conn.sendall(json.dumps(response).encode('utf-8'))
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()

def start_tracker():
    tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tracker_socket.bind((TRACKER_HOST, TRACKER_PORT))
    tracker_socket.listen()
    print(f"Tracker running on {TRACKER_HOST}:{TRACKER_PORT}")

    while True:
        conn, addr = tracker_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_tracker()

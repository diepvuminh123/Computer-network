# tracker.py
import socket
import json
import threading

TRACKER_HOST = 'localhost'
TRACKER_PORT = 55555
file_registry = {}

def handle_client(connection, address):
    try:
        data = connection.recv(1024).decode('utf-8')
        request = json.loads(data)
        action = request.get("action")

        if action == "register":
            file_name = request.get("file_name")
            piece_index = request.get("piece_index")
            peer_info = (address[0], request.get("peer_port"))
            
            if file_name not in file_registry:
                file_registry[file_name] = {}
            if piece_index not in file_registry[file_name]:
                file_registry[file_name][piece_index] = []
            if peer_info not in file_registry[file_name][piece_index]:
                file_registry[file_name][piece_index].append(peer_info)
            connection.sendall(json.dumps({"status": "registered"}).encode('utf-8'))

        elif action == "get_peers":
            file_name = request.get("file_name")
            piece_index = request.get("piece_index")
            peers = file_registry.get(file_name, {}).get(piece_index, [])
            connection.sendall(json.dumps({"peers": peers}).encode('utf-8'))

    except Exception as e:
        print(f"Error handling client {address}: {e}")
    finally:
        connection.close()

def start_tracker():
    tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tracker_socket.bind((TRACKER_HOST, TRACKER_PORT))
    tracker_socket.listen()
    print(f"Tracker is running on {TRACKER_HOST}:{TRACKER_PORT}")

    while True:
        conn, addr = tracker_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_tracker()

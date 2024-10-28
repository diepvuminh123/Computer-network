# peer.py
import socket
import threading
import os

def handle_peer_connection(conn, addr, file_hash):
    print(f"Connected by {addr}")
    requested_file = conn.recv(1024).decode('utf-8')
    
    if requested_file == file_hash and os.path.exists(file_hash):
        with open(file_hash, 'rb') as f:
            data = f.read()
            conn.sendall(data)
            print(f"Sent file {file_hash} to {addr}")
    else:
        print(f"File {requested_file} not found for {addr}")
    conn.close()

def run_peer_server(port, file_hash):
    # Server to handle incoming peer requests
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', port))
        s.listen()
        print(f"Peer server listening on port {port}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_peer_connection, args=(conn, addr, file_hash)).start()

if __name__ == "__main__":
    file_hash = "sample_file_hash"  # Replace with actual file hash
    port = 9000
    run_peer_server(port, file_hash)

# server.py
import socket
import threading
import os
import hashlib
import json

SHARED_DIR = "shared_files"
os.makedirs(SHARED_DIR, exist_ok=True)
PEER_PORT = 50001

def read_file_in_chunks(file_path, output_dir, chunk_size=1024):
    """
    Reads a file in chunks, calculates a hash for each chunk, and saves
    each piece in the specified output directory.
    """
    file_name = os.path.basename(file_path)
    os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists
    
    with open(file_path, 'rb') as f:
        piece_num = 0
        while chunk := f.read(chunk_size):
            # Calculate the hash for the current chunk (for verification)
            piece_hash = hashlib.sha1(chunk).hexdigest()
            # Define the output path for each chunk
            part_path = os.path.join(output_dir, f"{file_name}.chunk_{piece_num}")
            
            # Write the chunk to a file in the output directory
            with open(part_path, 'wb') as part_file:
                part_file.write(chunk)
            
            print(f"Saved piece {piece_num} as {part_path} with hash {piece_hash}")
            piece_num += 1

def handle_download_request(conn, addr):
    try:
        data = conn.recv(1024).decode('utf-8')
        request = json.loads(data)
        if request["action"] == "download":
            file_name = request["file_name"]
            piece_index = request["piece_index"]
            part_path = os.path.join(SHARED_DIR, f"{file_name}.chunk_{piece_index}")

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
    file_path = "C:\\Users\\MSI\\Pictures\\R6 ATTACK GUIde\\OREGON_basement_1.jpg"  # Path to the file to be shared
    read_file_in_chunks(file_path, output_dir=SHARED_DIR, chunk_size=1024)
    start_peer_server()

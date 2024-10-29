import socket
import json
import threading
import os
import shutil

TRACKER_HOST = 'localhost'
TRACKER_PORT = 5000
NODE_PORT = 6001  # Thay đổi cổng này cho mỗi node
SHARED_FILES_DIR = "shared_files"
DOWNLOADED_FILES_DIR = "downloaded_files"

os.makedirs(SHARED_FILES_DIR, exist_ok=True)
os.makedirs(DOWNLOADED_FILES_DIR, exist_ok=True)

def split_file(file_path, chunk_size=1024):
    file_name = os.path.basename(file_path)
    file_parts = []
    with open(file_path, 'rb') as f:
        part_num = 0
        while chunk := f.read(chunk_size):
            part_file = os.path.join(SHARED_FILES_DIR, f"{file_name}_part_{part_num}")
            with open(part_file, 'wb') as part:
                part.write(chunk)
            file_parts.append((file_name, part_num))
            part_num += 1
    return file_parts

def register_piece_with_tracker(file_name, piece_index):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((TRACKER_HOST, TRACKER_PORT))
            request = {
                "action": "register",
                "file_name": file_name,
                "piece_index": piece_index,
                "peer_port": NODE_PORT
            }
            sock.sendall(json.dumps(request).encode('utf-8'))
            response = json.loads(sock.recv(1024).decode('utf-8'))
            print("Tracker response:", response)
    except Exception as e:
        print(f"Error: {e}")

def get_peers_for_piece(file_name, piece_index):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((TRACKER_HOST, TRACKER_PORT))
            request = {
                "action": "get_peers",
                "file_name": file_name,
                "piece_index": piece_index
            }
            sock.sendall(json.dumps(request).encode('utf-8'))
            response = json.loads(sock.recv(1024).decode('utf-8'))
            return response.get("peers", [])
    except Exception as e:
        print(f"Error: {e}")
        return []

def download_piece_from_peer(peer_ip, peer_port, file_name, piece_index):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((peer_ip, peer_port))
            request = {
                "action": "download",
                "file_name": file_name,
                "piece_index": piece_index
            }
            sock.sendall(json.dumps(request).encode('utf-8'))
            
            piece_data = sock.recv(1024)
            part_path = os.path.join(DOWNLOADED_FILES_DIR, f"{file_name}_part_{piece_index}")
            with open(part_path, "wb") as f:
                f.write(piece_data)
            print(f"Downloaded part {piece_index} of '{file_name}' from {peer_ip}:{peer_port}")
    except Exception as e:
        print(f"Error: {e}")

def assemble_file(file_name, total_parts):
    output_path = os.path.join(DOWNLOADED_FILES_DIR, file_name)
    with open(output_path, 'wb') as output_file:
        for part_num in range(total_parts):
            part_path = os.path.join(DOWNLOADED_FILES_DIR, f"{file_name}_part_{part_num}")
            if not os.path.exists(part_path):
                print(f"Missing part {part_num}, file cannot be assembled completely.")
                return False
            with open(part_path, 'rb') as part_file:
                output_file.write(part_file.read())
    print(f"File '{file_name}' has been successfully assembled at '{output_path}'.")
    return True

def start_peer_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', NODE_PORT))
    server_socket.listen(5)
    print(f"Peer server running on port {NODE_PORT}")

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_peer_request, args=(conn, addr)).start()

def create_file_copy(original_path, copy_path):
    shutil.copyfile(original_path, copy_path)

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File {file_path} has been deleted.")
    else:
        print(f"File {file_path} does not exist.")

def handle_peer_request(conn, addr):
    try:
        request = json.loads(conn.recv(1024).decode('utf-8'))
        action = request.get("action")
        
        if action == "download":
            file_name = request.get("file_name")
            piece_index = request.get("piece_index")
            file_path = os.path.join(SHARED_FILES_DIR, f"{file_name}_part_{piece_index}")

            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    conn.sendall(f.read())
            else:
                conn.sendall(b"")
    except Exception as e:
        print(f"Error handling peer request from {addr}: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    original_file_path = "C:\\Users\\Admin\\Downloads\\config_sequence.png"  # Đường dẫn tệp PDF gốc
    copied_file_path = "C:\\Users\\Admin\\Downloads\\config_sequence_copy.png" # Đường dẫn tệp PDF sao chép
    
    # Tạo bản sao của tệp PDF gốc
    create_file_copy(original_file_path, copied_file_path)
    
    # Chia nhỏ tệp sao chép thành các phần
    parts = split_file(copied_file_path)
    
    for file_name, part_num in parts:
        register_piece_with_tracker(file_name, part_num)

    threading.Thread(target=start_peer_server).start()
    
    for file_name, part_num in parts:
        peers = get_peers_for_piece(file_name, part_num)
        for peer in peers:
            peer_ip, peer_port = peer
            download_piece_from_peer(peer_ip, peer_port, file_name, part_num)
    
    # Sau khi tải xuống, thử ghép các phần lại với nhau
    assemble_file(copied_file_path, len(parts))

    # Delete the copied file after reassembling
    delete_file(copied_file_path)
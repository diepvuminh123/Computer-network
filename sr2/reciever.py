# client.py
import socket
import json
import os
import threading

TRACKER_HOST = 'localhost'
TRACKER_PORT = 55555
PEER_PORT = 50001
SHARED_DIR = "shared_files"
DOWNLOADED_DIR = "downloaded_files"
os.makedirs(SHARED_DIR, exist_ok=True)
os.makedirs(DOWNLOADED_DIR, exist_ok=True)

def register_piece_with_tracker(file_name, piece_index):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((TRACKER_HOST, TRACKER_PORT))
            request = {
                "action": "register",
                "file_name": file_name,
                "piece_index": piece_index,
                "peer_port": PEER_PORT
            }
            sock.sendall(json.dumps(request).encode('utf-8'))
            response = json.loads(sock.recv(1024).decode('utf-8'))
            print("Tracker response:", response)
    except Exception as e:
        print(f"Error: {e}")

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
            if piece_data:
                part_path = os.path.join(DOWNLOADED_DIR, f"{file_name}_part_{piece_index}")
                with open(part_path, "wb") as f:
                    f.write(piece_data)
                print(f"Downloaded part {piece_index} from {peer_ip}:{peer_port}")
    except Exception as e:
        print(f"Error: {e}")

def parallel_download(file_name, total_parts):
    threads = []
    for part_num in range(total_parts):
        peers = get_peers_for_piece(file_name, part_num)
        if peers:
            for peer in peers[:2]:  # Limit to 2 parallel downloads
                peer_ip, peer_port = peer
                t = threading.Thread(target=download_piece_from_peer, args=(peer_ip, peer_port, file_name, part_num))
                t.start()
                threads.append(t)

    for t in threads:
        t.join()
    print("Download completed.")

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

if __name__ == "__main__":
    file_name = "sample_file"
    total_parts = 5  # Example number of parts
    for i in range(total_parts):
        register_piece_with_tracker(file_name, i)

    parallel_download(file_name, total_parts)

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
            # Register the piece with .chunk_{piece_index} format
            request = {
                "action": "register",
                "file_name": f"{file_name}.chunk_{piece_index}",
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
            # Request with .chunk_{piece_index} format
            request = {
                "action": "download",
                "file_name": f"{file_name}.chunk_{piece_index}",
                "piece_index": piece_index
            }
            sock.sendall(json.dumps(request).encode('utf-8'))
            piece_data = sock.recv(1024)
            if piece_data:
                part_path = os.path.join(DOWNLOADED_DIR, f"{file_name}.chunk_{piece_index}")
                with open(part_path, "wb") as f:
                    f.write(piece_data)
                print(f"Downloaded part {piece_index} from {peer_ip}:{peer_port}")
    except Exception as e:
        print(f"Error: {e}")

def parallel_download(file_name, total_parts, output_dir):
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

    # Assemble the downloaded parts after download completes
    assemble_file(file_name, total_parts, output_dir)

def get_peers_for_piece(file_name, piece_index):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((TRACKER_HOST, TRACKER_PORT))
            # Request with .chunk_{piece_index} format
            request = {
                "action": "get_peers",
                "file_name": f"{file_name}.chunk_{piece_index}",
                "piece_index": piece_index
            }
            sock.sendall(json.dumps(request).encode('utf-8'))
            response = json.loads(sock.recv(1024).decode('utf-8'))
            return response.get("peers", [])
    except Exception as e:
        print(f"Error: {e}")
        return []

def assemble_file(file_name, total_parts, output_dir):
    os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists
    output_file_path = os.path.join(output_dir, file_name)
    with open(output_file_path, 'wb') as output_file:
        for part_num in range(total_parts):
            # Access each piece with .chunk_{piece_index} format
            part_path = os.path.join(DOWNLOADED_DIR, f"{file_name}.chunk_{part_num}")
            if os.path.exists(part_path):
                with open(part_path, 'rb') as piece_file:
                    output_file.write(piece_file.read())
                os.remove(part_path)  # Delete the part after writing to the final file
                print(f"Added {part_path} to {output_file_path} and deleted part")
            else:
                print(f"Missing part {part_num}: {part_path} not found.")
    print(f"File assembled successfully as {output_file_path}")

if __name__ == "__main__":
    file_name = "OREGON_basement_1.jpg"
    total_parts = 600  # Example number of parts
    output_dir = DOWNLOADED_DIR

    # Register each piece with the tracker using .chunk_{piece_index} format
    for i in range(total_parts):
        register_piece_with_tracker(file_name, i)

    # Download and assemble the file
    parallel_download(file_name, total_parts, output_dir)

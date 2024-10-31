import socket
import threading
import json
import os
import time

TRACKER_HOST = "localhost"
TRACKER_PORT = 5000
PEER_PORT = None  # Mỗi client sẽ có một cổng riêng
total_pieces = None

# Đọc file torrent
def read_torrent_file(torrent_file):
    global total_pieces
    with open(torrent_file, "r") as f:
        torrent_info = json.load(f)
    total_pieces = len(torrent_info["pieces"])
    return torrent_info

torrent_info = read_torrent_file("AAA.torrent")
file_name = torrent_info["file_name"]

# Đăng ký với tracker
def register_with_tracker(pieces):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((TRACKER_HOST, TRACKER_PORT))
        register_request = {
            "type": "register",
            "file_name": file_name,
            "pieces": pieces,
            "port": PEER_PORT
        }
        s.send(json.dumps(register_request).encode())
        response = s.recv(1024).decode()
        print(response)

# Tải mảnh từ peer và hiển thị tiến trình tải
def download_piece_from_peer(peer_info, piece_index):
    try:
        print(f"Starting download of piece {piece_index} from {peer_info['address']}:{peer_info['port']}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((peer_info["address"], peer_info["port"]))
            request = {"type": "download_piece", "piece_index": piece_index}
            s.send(json.dumps(request).encode())
            data = s.recv(1024).decode()
            
            # Ghi dữ liệu mảnh vào file
            with open(f"{file_name}_piece_{piece_index}", "wb") as f:
                f.write(data.encode())
            
            print(f"Downloaded piece {piece_index} from {peer_info['address']}:{peer_info['port']}")

    except Exception as e:
        print(f"Failed to download piece {piece_index} from {peer_info['address']}:{peer_info['port']}. Error: {e}")

# Lấy danh sách peer có mảnh cần tải
def request_peers_for_piece(piece_index):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((TRACKER_HOST, TRACKER_PORT))
        request = {"type": "request_peers", "file_name": file_name, "piece_index": piece_index}
        s.send(json.dumps(request).encode())
        response = s.recv(1024).decode()
        return json.loads(response)

# Tải các mảnh còn thiếu
def download_missing_pieces(missing_pieces):
    threads = []

    for piece_index in missing_pieces:
        peers_with_piece = request_peers_for_piece(piece_index)
        if peers_with_piece:
            peer = peers_with_piece[0]  # Chọn một peer để tải
            thread = threading.Thread(target=download_piece_from_peer, args=(peer, piece_index))
            threads.append(thread)
            thread.start()

    # Đợi tất cả các thread tải xong
    for thread in threads:
        thread.join()

    print("All pieces downloaded. Reconstructing file...")

# Ghép các mảnh thành file hoàn chỉnh
def reconstruct_file():
    with open(f"{file_name}_downloaded.pdf", "wb") as final_file:
        for i in range(total_pieces):
            with open(f"{file_name}_piece_{i}", "rb") as piece_file:
                final_file.write(piece_file.read())
    print("File reconstruction complete. Saved as AAA_downloaded.pdf.")

# Cấu hình cho từng client
if __name__ == "__main__":
    client_type = int(input("Enter client type (1, 2, or 3): "))

    if client_type == 1:
        pieces = list(range(total_pieces // 2))
        PEER_PORT = 6001
    elif client_type == 2:
        pieces = list(range(total_pieces // 2, total_pieces))
        PEER_PORT = 6002
    else:
        pieces = []
        missing_pieces = list(range(total_pieces))
        PEER_PORT = 6003

    register_with_tracker(pieces)
    
    if client_type == 3:
        download_missing_pieces(missing_pieces)
        reconstruct_file()

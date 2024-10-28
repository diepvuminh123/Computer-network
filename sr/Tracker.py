import socket
import threading
import json

# Cấu hình địa chỉ và cổng cho Tracker
TRACKER_HOST = 'localhost'
TRACKER_PORT = 5000

# Tạo dictionary để lưu trữ thông tin tệp và các peer
files = {}

# Hàm xử lý kết nối từ các peer
def handle_peer_connection(connection, address):
    try:
        data = connection.recv(1024).decode('utf-8')
        if not data:
            return
        
        request = json.loads(data)
        action = request.get("action")
        
        if action == "register":
            # Đăng ký thông tin peer và phần tệp mà nó có
            file_name = request.get("file_name")
            piece_index = request.get("piece_index")
            peer_info = (address[0], request.get("peer_port"))

            if file_name not in files:
                files[file_name] = {}
            if piece_index not in files[file_name]:
                files[file_name][piece_index] = []

            # Thêm peer vào danh sách nếu chưa tồn tại
            if peer_info not in files[file_name][piece_index]:
                files[file_name][piece_index].append(peer_info)
            
            response = {"status": "success", "message": "Peer registered successfully."}
            connection.sendall(json.dumps(response).encode('utf-8'))

        elif action == "get_peers":
            # Trả về danh sách peer có phần tệp yêu cầu
            file_name = request.get("file_name")
            piece_index = request.get("piece_index")

            if file_name in files and piece_index in files[file_name]:
                peers = files[file_name][piece_index]
                response = {"status": "success", "peers": peers}
            else:
                response = {"status": "error", "message": "No peers found for requested piece."}

            connection.sendall(json.dumps(response).encode('utf-8'))
    except Exception as e:
        print(f"Error handling peer {address}: {e}")
    finally:
        connection.close()

# Hàm để khởi chạy tracker
def start_tracker():
    tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tracker_socket.bind((TRACKER_HOST, TRACKER_PORT))
    tracker_socket.listen(5)
    print(f"Tracker is running on {TRACKER_HOST}:{TRACKER_PORT}")

    while True:
        conn, addr = tracker_socket.accept()
        print(f"Connected by {addr}")
        thread = threading.Thread(target=handle_peer_connection, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_tracker()
# testing
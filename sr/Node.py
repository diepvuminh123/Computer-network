import socket
import json
# Cấu hình địa chỉ Tracker và Node
TRACKER_HOST = 'localhost'
TRACKER_PORT = 5000
NODE_HOST = 'localhost'
NODE_PORT = 6000  # Cổng riêng của node này

def register_with_tracker(file_name, piece_index):
    try:
        # Kết nối đến Tracker
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((TRACKER_HOST, TRACKER_PORT))
            
            # Tạo yêu cầu đăng ký và gửi đến Tracker
            request = {
                "action": "register",
                "file_name": file_name,
                "piece_index": piece_index,
                "peer_port": NODE_PORT
            }
            sock.sendall(json.dumps(request).encode('utf-8'))

            # Nhận phản hồi từ Tracker
            response = sock.recv(1024).decode('utf-8')
            response = json.loads(response)
            print("Tracker response:", response)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    file_name = "example_file.txt"
    piece_index = 1  # Giả sử node này có phần thứ nhất của tệp
    register_with_tracker(file_name, piece_index)

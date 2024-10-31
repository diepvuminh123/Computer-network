import socket
import threading
import json

# Lưu trữ thông tin về các peer và các mảnh mà mỗi peer có
peers_info = {}

# Hàm xử lý từng kết nối từ node
def handle_client_connection(client_socket, client_address):
    try:
        data = client_socket.recv(1024).decode()
        request = json.loads(data)
        
        if request["type"] == "register":
            file_name = request["file_name"]
            pieces = request["pieces"]
            
            if file_name not in peers_info:
                peers_info[file_name] = []
            
            # Lưu thông tin peer và các mảnh nó sở hữu
            peers_info[file_name].append({
                "address": client_address[0],
                "port": request["port"],
                "pieces": pieces
            })
            client_socket.send("Registration successful".encode())
        
        elif request["type"] == "request_peers":
            file_name = request["file_name"]
            piece_index = request["piece_index"]
            # Tìm các peer có mảnh này
            peers_with_piece = [
                peer for peer in peers_info.get(file_name, [])
                if piece_index in peer["pieces"]
            ]
            client_socket.send(json.dumps(peers_with_piece).encode())
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def start_tracker():
    tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tracker_socket.bind(("0.0.0.0", 5000))
    tracker_socket.listen(5)
    print("Tracker server started on port 5000")
    
    while True:
        client_socket, client_address = tracker_socket.accept()
        client_handler = threading.Thread(
            target=handle_client_connection, args=(client_socket, client_address)
        )
        client_handler.start()

if __name__ == "__main__":
    start_tracker()

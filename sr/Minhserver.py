# Minhserver.py
import socket
import threading
import time

# Thiết lập thông tin tracker
host = 'localhost'
port = 4000
tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tracker.bind((host, port))
tracker.listen(5)
print("Tracker server listening on port", port)

# Lưu trữ thông tin các peer
peers = {}

# Hàm xử lý kết nối từ client
def handle_client(conn, addr):
    print("Connected by", addr)
    try:
        # Nhận dữ liệu từ client
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break  # Exit if no more data is received
            
            if data == "REQUEST":
                # Gửi danh sách các peer cho client
                peer_list = ""
                for info_hash, peer_list_data in peers.items():
                    peer_list += f"File {info_hash}:\n"
                    for peer in peer_list_data:
                        ip, port, peer_id = peer
                        peer_list += f"  Peer ID: {peer_id}, IP: {ip}, Port: {port}\n"
                conn.sendall(peer_list.encode())
            else:
                # Dữ liệu chứa thông tin `info_hash`, `peer_id`, và `port` của client
                info_hash, peer_id, client_port = data.split(',')
                # Lưu thông tin vào danh sách peer cho từng file (dựa trên `info_hash`)
                if info_hash not in peers:
                    peers[info_hash] = []
                peers[info_hash].append((addr[0], int(client_port), peer_id))
                conn.send(b"Registered successfully!")
                print(f"Peer {peer_id} at {addr} registered for file {info_hash}.")
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()

# Chấp nhận kết nối từ nhiều client đồng thời
while True:
    conn, addr = tracker.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()

# Function to print all registered peers
def print_peers():
    while True:
        print("\nCurrent list of peers:")
        for info_hash, peer_list in peers.items():
            print(f"File (info_hash: {info_hash}):")
            for peer in peer_list:
                ip, port, peer_id = peer
                print(f"  Peer ID: {peer_id}, IP: {ip}, Port: {port}")
        print("\n--------------------------------")
        time.sleep(10)  # Print every 10 seconds

# Start a separate thread to print peers periodically
threading.Thread(target=print_peers, daemon=True).start()

import socket
import threading

# Khởi tạo server
host = 'localhost'
port = 4000
tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tracker.bind((host, port))
tracker.listen(5)
print("Tracker server listening on port", port)

# Lưu thông tin các peer
peers = {}

# Hàm xử lý kết nối từ các peer
def handle_client(conn, addr):
    print("Connected by", addr)
    try:
        # Nhận thông báo "REGISTER" hoặc "REQUEST" từ client
        message = conn.recv(1024).decode()
        if message == "REGISTER":
            peers[addr] = conn
            conn.send(b"Registered successfully!")
            print(f"Peer {addr} registered.")
        
        elif message == "REQUEST":
            # Gửi danh sách các peer hiện có cho client
            peer_list = "\n".join([f"{str(peer[0])}:{peer[1]}" for peer in peers.keys() if peer != addr])
            conn.send(peer_list.encode())
            print(f"Sent peer list to {addr}")
        
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    #finally:
     #   conn.close()
      #  if addr in peers:
       #     del peers[addr]
        #    print(f"Peer {addr} disconnected and removed from the list.")

# Chấp nhận nhiều client kết nối
while True:
    conn, addr = tracker.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()

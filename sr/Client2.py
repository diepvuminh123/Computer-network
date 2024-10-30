import socket

# Khởi tạo kết nối tới tracker
tracker_host = 'localhost'
tracker_port = 4000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((tracker_host, tracker_port))

# Đăng ký với tracker
client.send(b"REGISTER")
response = client.recv(1024).decode()
print("Tracker Response:", response)

# Yêu cầu danh sách các peer
client.send(b"REQUEST")
peer_list = client.recv(1024).decode()
print("Peer List:")
print(peer_list)

# Đóng kết nối sau khi hoàn thành
client.close()

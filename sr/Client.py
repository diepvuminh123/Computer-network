import socket

# Khởi tạo kết nối tới tracker
tracker_host = 'localhost'
tracker_port = 4000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((tracker_host, tracker_port))

# Đăng ký với tracker

print("Hello")
client.close()

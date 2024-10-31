import tkinter as tk
from tkinter import filedialog, messagebox
import socket
import os
import threading
import time
import select

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TCP Client")

        # Giao diện người dùng
        self.ip_label = tk.Label(root, text="Server IP:")
        self.ip_entry = tk.Entry(root)
        self.ip_entry.insert(0, "127.0.0.1")  # Sử dụng localhost để kiểm tra

        self.port_label = tk.Label(root, text="Server Port:")
        self.port_entry = tk.Entry(root)
        self.port_entry.insert(0, "6789")  # Cổng mặc định cho server
        
        self.connect_button = tk.Button(root, text="Connect", command=self.connect_to_server)
        self.send_button = tk.Button(root, text="Send File Path", command=self.send_file_path)
        self.get_list_button = tk.Button(root, text="Get File List", command=self.get_file_list)
        self.folder_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=70)
        self.download_button = tk.Button(root, text="Download File", command=self.download_file)

        self.ip_label.pack(padx=10, pady=5)
        self.ip_entry.pack(padx=10, pady=5)
        self.port_label.pack(padx=10, pady=5)
        self.port_entry.pack(padx=10, pady=5)
        self.connect_button.pack(padx=10, pady=5)
        self.send_button.pack(padx=10, pady=5)
        self.get_list_button.pack(padx=10, pady=5)
        self.folder_listbox.pack(padx=10, pady=5)
        self.download_button.pack(padx=10, pady=5)

        # Khởi tạo socket và các biến cần thiết
        self.client_socket = None
        self.download_socket = None

    def connect_to_server(self):
        # Kết nối đến máy chủ tracker
        server_ip = self.ip_entry.get()
        server_port = int(self.port_entry.get())
        if not server_ip or not server_port:
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((server_ip, server_port))
            self.folder_listbox.delete(0, tk.END)
            print("Connected to server.")
        except Exception as e:
            print(f"Error: {e}")
            self.client_socket.close() if self.client_socket else None

    def send_file_path(self):
        # Gửi đường dẫn tệp đến máy chủ tracker
        if self.client_socket:
            file_path = filedialog.askopenfilename()  
            if file_path:
                listen_port = self.open_listen_port(0)
                if listen_port:
                    self.client_socket.send(f"{file_path}:{listen_port}".encode('utf-8'))
                    print(f"Sent file path and port {listen_port} to server.")
                else:
                    print("Error opening listen port")
            else:
                print("No file selected")

    def open_listen_port(self, port):
        # Mở cổng lắng nghe để nhận tệp
        try:
            self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.listen_socket.bind(('0.0.0.0', port))
            actual_port = self.listen_socket.getsockname()[1]
            self.listen_socket_thread = threading.Thread(target=self.listen_for_messages)
            self.listen_socket_thread.daemon = True  
            self.listen_socket_thread.start()
            return actual_port
        except Exception as e:
            print(f"Error opening listen port: {e}")
        return None

    def listen_for_messages(self):
        # Lắng nghe thông báo từ các peers khác
        if not hasattr(self, 'listen_socket'):
            print("Listen socket is not open.")
            return

        while True:
            try:
                data, addr = self.listen_socket.recvfrom(1024)
                message = data.decode('utf-8')
                print(f"Received message from {addr}: {message}")
                if message.startswith('/'):
                    file_path = message
                    self.send_file(file_path, addr)
            except Exception as e:
                print(f"Error receiving message: {e}")

    def send_file(self, file_path, addr):
        # Gửi tệp đến peer yêu cầu
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as file:
                    data = file.read(1024)
                    while data:
                        self.listen_socket.sendto(data, addr)
                        data = file.read(1024)
                        time.sleep(0.1)
                    print(f"File '{file_path}' sent successfully to {addr}")
            except Exception as e:
                print(f"Error sending file: {e}")
        else:
            print(f"File '{file_path}' does not exist.")

    def get_file_list(self):
        # Yêu cầu danh sách tệp từ tracker
        if self.client_socket:
            self.client_socket.send("GET_DATA".encode('utf-8'))
            files = self.client_socket.recv(1024).decode('utf-8')
            self.display_file_list(files)
            print("List of files on the server:")
            print(files)

    def display_file_list(self, file_list):
        # Hiển thị danh sách tệp lên Listbox
        self.folder_listbox.delete(0, tk.END)
        files = file_list.split("\n")
        for file in files:
            self.folder_listbox.insert(tk.END, file)

    def get_file(self, addr, remote_file_path):
        # Nhận tệp từ peer
        try:
            filename = os.path.basename(remote_file_path)
            with open(filename, 'wb') as file:
                while True:
                    ready = select.select([self.download_socket], [], [], 5)
                    if ready[0]:
                        data, addr = self.download_socket.recvfrom(1024)
                        if not data:
                            break
                        file.write(data)
                    else:
                        print(f"Timeout while receiving file from {addr}")
                        break
                print(f"File received from {addr} and saved as '{filename}'")
        except Exception as e:
                print(f"Error receiving file: {e}")

    def download_file(self):
        # Tải tệp được chọn từ Listbox
        if self.client_socket:
            selected_item = self.folder_listbox.get(tk.ACTIVE) 
            if selected_item:
                parts = selected_item.split(',')
                if len(parts) == 3:
                    remote_ip = parts[0]
                    remote_port = int(parts[2])
                    remote_file_path = parts[1].strip() 
                    if not remote_ip or not remote_port or not remote_file_path:
                        messagebox.showerror("Lỗi", "Vui lòng nhập IP, Cổng và Đường dẫn tệp.")
                    self.download_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    self.download_socket.sendto(remote_file_path.encode('utf-8'), (remote_ip, remote_port))
                    self.get_file((remote_ip, remote_port), remote_file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()

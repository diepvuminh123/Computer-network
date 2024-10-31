import tkinter as tk
from tkinter import ttk  
import socket
import threading
import os

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TCP Server")

        self.tree = ttk.Treeview(root, columns=("#1", "#2", "#3", "#4"))
        self.tree.heading("#1", text="IP Client")
        self.tree.heading("#2", text="Port Client")
        self.tree.heading("#3", text="Message")
        self.tree.heading("#4", text="Port Download")
        self.tree.pack(padx=100, pady=50)
        
        self.start_button = tk.Button(root, text="Start Server", command=self.start_server)
        self.start_button.pack(pady=10)
        
        self.check_ip_entry = tk.Entry(root, width=15)
        self.check_ip_entry.insert(0, "IP to Check")
        self.check_ip_entry.pack(pady=10)
        
        self.check_button = tk.Button(root, text="Check IP Connection", command=self.check_connection_ip)
        self.check_button.pack(pady=10)

        self.server_socket = None
        self.running = False
        self.thread = None
        self.connected_clients = {}
        root.protocol("WM_DELETE_WINDOW", self.handle_window_close)
        
    def start_server(self):
        if not self.running:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('0.0.0.0', 6789))
            self.server_socket.listen(5)
            self.running = True
            self.thread = threading.Thread(target=self.accept_connections)
            self.thread.start()
            self.start_button.config(text="Stop Server")
        else:
            self.running = False
            self.server_socket.close()
            self.thread.join()
            self.start_button.config(text="Start Server")

    def accept_connections(self):
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                ip = f"{client_address[0]}:{client_address[1]}"
                ip_client = client_address[0]
                port_connect = client_address[1]
                self.connected_clients[ip] = client_socket
                
                item = self.tree.insert("", "end", values=(ip_client, port_connect, "No message", "No message"))
                data = client_socket.recv(1024).decode('utf-8')

                if data == "GET_DATA":
                    self.send_client_data(client_socket)  
                else:
                    parts = data.rsplit(":", 1)
                    if len(parts) == 2:
                        path = parts[0]
                        port = parts[1]
                        self.tree.item(item, values=(ip_client, port_connect, path, port))
                        with open("client_data.txt", "a") as file:
                            file.write(f"{ip_client}, {path}, {port}\n")
                    else:
                        self.tree.item(item, values=(ip_client, port_connect, data, "Invalid format"))

                client_socket.close()
            except OSError:
                break
            self.cleanup_connections()

    def cleanup_connections(self):
        to_remove = []
        for ip, client_socket in self.connected_clients.items():
            if not self.is_socket_connected(client_socket):
                to_remove.append(ip)

        for ip in to_remove:
            self.connected_clients.pop(ip)

    def is_socket_connected(self, sock):
        try:
            sock.send(b"")
            return True
        except (OSError, socket.error):
            return False

    def check_connection_ip(self):
        ip_to_check = self.check_ip_entry.get()
        try:
            ip, port = ip_to_check.split(":")
            if self.is_client_connected(ip, int(port)):
                print(f"{ip_to_check} is Alive")
            else:
                print(f"{ip_to_check} is Not Alive")
        except (ValueError, OSError):
            print(f"Invalid IP:Port: {ip_to_check}")

    def send_client_data(self, client_socket):
        try:
            with open("client_data.txt", "r") as file:
                data = file.read()
                client_socket.send(data.encode('utf-8'))
        except FileNotFoundError:
            client_socket.send("No data available.".encode('utf-8'))

    def handle_window_close(self):
        if self.running:
            self.running = False
            self.server_socket.close()
            self.thread.join()
            self.delete_client_data_file()
        root.destroy()

    def delete_client_data_file(self):
        try:
            os.remove("client_data.txt")
            print("Deleted client_data.txt")
        except FileNotFoundError:
            print("client_data.txt does not exist.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerApp(root)
    root.mainloop()

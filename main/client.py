from tkinter import *
import socket
from tkinter import filedialog
from tkinter import messagebox
import os
import threading
import _thread
from functools import partial

FILESIZE = 40960000
WINDOWSIZESTRING = "450x200+500+200"

# Tạo file lưu info các tài khoảng
if not os.path.exists("accounts.txt"):
    open("accounts.txt", "w").close()

# Mở giao diện chính sau khi đăng nhập thành công
def open_main_window():
    main_root.destroy() 
    main_window()

def register():
    # Đăng ký
    def register_user():
        username_info = username_entry.get()
        password_info = password_entry.get()

        if username_info == "" or password_info == "":
            messagebox.showerror("Error", "The username or password field is empty.")
            return

        with open("accounts.txt", "r") as file:
            list = file.readlines()
            for account in list:
                stored_username, _ = account.strip().split(":")
                if stored_username == username_info:
                    messagebox.showerror("Error", "Username already exists.")
                    return

        with open("accounts.txt", "a") as file:
            file.write(f"{username_info}:{password_info}\n")
        
        messagebox.showinfo("Succeeded", "Registered successfully! You can now login.")
        register_window.destroy()

    # Cửa sổ đăng ký
    register_window = Toplevel(main_root)
    register_window.title("Register")
    register_window.geometry("300x250")
    register_window.configure(bg="#FFFFF0")
    register_window.resizable(False, False)

    Label(register_window, text="Sign up", font=("Segoe UI", 20, 'bold'), bg="#FFFFF0", fg="#800020").pack(pady=10)
    Label(register_window, text="Username", font=("Segoe UI", 13), bg="#FFFFF0").pack()
    username_entry = Entry(register_window, width=20, bg="white", font=("arial", 15))
    username_entry.pack()

    Label(register_window, text="Password", font=("Segoe UI", 13), bg="#FFFFF0").pack()
    password_entry = Entry(register_window, width=20, bg="white", font=("arial", 15), show="*")
    password_entry.pack()

    Button(register_window, text="Register", font=("Segoe UI", 15, 'bold'), bg="#FFFFF0", fg="#800020",
           command=register_user).pack(pady=20)
    
# Xử lý đăng nhập
def login():
    username_info = username_entry.get()
    password_info = password_entry.get()

    with open("accounts.txt", "r") as file:
        list = file.readlines()
        for account in list:
            stored_username, stored_password = account.strip().split(":")
            if stored_username == username_info and stored_password == password_info:
                open_main_window()
                return

    messagebox.showerror("Error", "Username or password is incorrect.")

# Giao diện chính sau khi đăng nhập
def main_window():
    root = Tk()
    root.title("P2P FILE TRANSFER CLIENT")
    root.geometry(WINDOWSIZESTRING)
    root.configure(bg="#FFFFF0")
    root.resizable(False, False)

    image_icon = PhotoImage(file="Image/app_icon.png")
    root.iconphoto(False, image_icon)

    IP = socket.gethostbyname(socket.gethostname())
    PORT = 4456
    DLPORT = 4444
    SIZE = 40960000
    FORMAT = "utf-8"
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    uploaded_files = []

    def receive_thread(filename):
        host_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host_client.bind((IP, DLPORT))
        host_client.listen()
        while True:
            friend, addr = host_client.accept()
            f = open("downloads/" + filename, "wb")
            l = friend.recv(SIZE)
            while l:
                f.write(l)
                l = friend.recv(SIZE)
            f.close()
            friend.close()
            messagebox.showinfo("Download", "File has been downloaded successfully.")
            break
        host_client.close()

    def share_thread(peer, port, file):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((peer, DLPORT))
        f = open(file[0], 'rb')
        l = f.read(SIZE)
        while l:
            client_socket.send(l)
            l = f.read(SIZE)
        f.close()
        client_socket.close()

    def select_file():
        filedir = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title='Select File',
            filetype=(('All Files', '*.*'),)
        )
        if filedir:
            name = os.path.basename(filedir)
            if name:
                uploaded_files.append((filedir, name))
                client.send(f"UPLOAD@{name}".encode(FORMAT))
                messagebox.showinfo("Uploaded", "File has been uploaded successfully.")

    def Upload():
        select_file()

    def FindFile(filename):
        for item in uploaded_files:
            if item[1] == filename:
                return True
        return False

    def GetFile(filename):
        ans = ("", "")
        for item in uploaded_files:
            if item[1] == filename:
                ans = item
        return ans

    def Download():
        download_window = Toplevel(root)
        download_window.title("Enter File Name to Download")
        download_window.geometry("300x150")
        download_window.configure(bg="#FFFFF0")
        download_window.resizable(False, False)

        Label(download_window, text="Enter file name:", font=('Segoe UI', 13), bg="#FFFFF0").pack(pady=10)
        file_name_entry = Entry(download_window, width=20, fg="black", border=2, bg='white', font=('arial', 15))
        file_name_entry.pack(pady=5)

        def start_download():
            fn = file_name_entry.get()
            if fn:
                send_msg = f"DOWNLOAD@{fn}"
                client.send(send_msg.encode(FORMAT))
                _thread.start_new_thread(partial(receive_thread, fn), ())
                download_window.destroy()  
                
        Button(download_window, text="Download", font=("Segoe UI", 13, 'bold'), bg="#FFFFF0", fg="#800020",
            command=start_download).pack(pady=10)
        
    def Connect():
        SERVERIP = ipInp.get()
        ADDRESS = (SERVERIP, PORT)
        client.connect(ADDRESS)
        messagebox.showinfo("Succeeded", "Connected to the server successfully.")
        _thread.start_new_thread(handle_server, ())
        
    Label(root, text="Server's IP address", font=('Segoe UI', 13), bg="#FFFFF0").place(x=75, y=20)
    ipInp = Entry(root, width=14, fg="black", border=2, bg='white', font=('arial', 20))
    ipInp.place(x=40, y=50)

    con = Button(root, text="CONNECT", font=('Segoe UI', 15, 'bold'), bg="#FFFFF0", fg="#800020",
                 activebackground="#005BB5", activeforeground="white", command=Connect)
    con.place(x=285, y=45)

    send = Button(root, text="UPLOAD", font=('Segoe UI', 15, 'bold'), bg="#FFFFF0", fg="#800020",
                  activebackground="#005BB5", activeforeground="white", command=Upload)
    send.place(x=60, y=120)

    receive = Button(root, text="DOWNLOAD", font=('Segoe UI', 15, 'bold'), bg="#FFFFF0", fg="#800020",
                     activebackground="#005BB5", activeforeground="white", command=Download)
    receive.place(x=260, y=120)

    def handle_server():
        while True:
            data = client.recv(SIZE).decode(FORMAT)
            temp = data.split("@")
            cmd = temp[0]
            if len(temp) > 1:
                msg = temp[1]
            if cmd == "DISCONNECTED":
                break
            elif cmd == "DOWNLOAD":
                file, peer, portstr = msg.split(";")
                port = int(portstr)
                if FindFile(file):
                    get = GetFile(file)
                    _thread.start_new_thread(partial(share_thread, peer, port, get), ())

    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()

# Cửa sổ đăng nhập
main_root = Tk()
main_root.title("Login")
main_root.geometry("320x320")
main_root.configure(bg="#FFFFF0")
main_root.resizable(False, False)

Label(main_root, text="Login", font=("Segoe UI", 20, 'bold'), bg="#FFFFF0", fg="#800020").pack(pady=10)
Label(main_root, text="Username", font=("Segoe UI", 13), bg="#FFFFF0").pack()
username_entry = Entry(main_root, width=20, bg="white", font=("arial", 15))
username_entry.pack()

Label(main_root, text="Password", font=("Segoe UI", 13), bg="#FFFFF0").pack()
password_entry = Entry(main_root, width=20, bg="white", font=("arial", 15), show="*")
password_entry.pack()

Button(main_root, text="Log in", font=("Segoe UI", 15, 'bold'), bg="#FFFFF0", fg="#800020", command=login).pack(pady=10)
Button(main_root, text="Sign up", font=("Segoe UI", 15, 'bold'), bg="#FFFFF0", fg="#800020", command=register).pack(pady=10)

main_root.mainloop()

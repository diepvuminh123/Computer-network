from tkinter import *
import socket
from tkinter import filedialog
from tkinter import messagebox
import os
import threading
import _thread
from functools import partial

FILESIZE = 40960000
WINDOWSIZESTRING = "450x500+500+200"

# Tạo file lưu tài khoản nếu chưa có
if not os.path.exists("accounts.txt"):
    open("accounts.txt", "w").close()

# Hàm mở giao diện chính sau khi đăng nhập thành công
def open_main_window():
    main_root.destroy()  # Đóng cửa sổ đăng nhập
    main_window()  # Mở cửa sổ chính

def register():
    # Hàm đăng ký
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
    register_window.configure(bg="#f4fdfe")
    register_window.resizable(False, False)

    Label(register_window, text="Sign up", font=("Acumin Variable Concept", 20, 'bold'), bg="#f4fdfe", fg="#003366").pack(pady=10)
    Label(register_window, text="Username", font=("Acumin Variable Concept", 13), bg="#f4fdfe").pack()
    username_entry = Entry(register_window, width=20, bg="white", font=("arial", 15))
    username_entry.pack()

    Label(register_window, text="Password", font=("Acumin Variable Concept", 13), bg="#f4fdfe").pack()
    password_entry = Entry(register_window, width=20, bg="white", font=("arial", 15), show="*")
    password_entry.pack()

    Button(register_window, text="Register", font=("Acumin Variable Concept", 15, 'bold'), bg="#f4fdfe", fg="#003366",
           command=register_user).pack(pady=20)

def login():
    # Hàm xử lý đăng nhập
    username_info = username_entry.get()
    password_info = password_entry.get()

    with open("accounts.txt", "r") as file:
        list = file.readlines()
        for account in list:
            stored_username, stored_password = account.strip().split(":")
            if stored_username == username_info and stored_password == password_info:
                open_main_window()  # Mở cửa sổ chính
                return

    messagebox.showerror("Error", "Username or password is incorrect.")

# Giao diện chính sau khi đăng nhập
def main_window():
    root = Tk()
    root.title("FILE TRANSFER CLIENT")
    root.geometry(WINDOWSIZESTRING)
    root.configure(bg="#f4fdfe")
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

    # Thêm Listbox để hiển thị danh sách file đã upload
    Label(root, text="Uploaded files list", font=('Acumin Variable Concept', 13), bg="#f4fdfe").place(x=20, y=240)
    uploaded_listbox = Listbox(root, width=45, height=10, font=('arial', 12))
    uploaded_listbox.place(x=20, y=275)

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
                messagebox.showinfo("Upload", f"'{name}' has been uploaded.")
                uploaded_listbox.insert(END, name)  # Hiển thị tên file trong danh sách

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

    #incoming_file = Entry(root, width=14, fg="black", border=2, bg='white', font=('arial', 20))
    #incoming_file.place(x=20, y=250)

    def Download():
        # Create a new Toplevel window for file name input
        download_window = Toplevel(root)
        download_window.title("Enter File Name to Download")
        download_window.geometry("300x150")
        download_window.configure(bg="#f4fdfe")
        download_window.resizable(False, False)

        # Label for the new window
        Label(download_window, text="Enter file name:", font=('Acumin Variable Concept', 13), bg="#f4fdfe").pack(pady=10)
        
        # Entry widget for file name input
        file_name_entry = Entry(download_window, width=20, fg="black", border=2, bg='white', font=('arial', 15))
        file_name_entry.pack(pady=5)

        # Function to handle the download after entering the file name
        def start_download():
            fn = file_name_entry.get()
            if fn:
                send_msg = f"DOWNLOAD@{fn}"
                client.send(send_msg.encode(FORMAT))
                _thread.start_new_thread(partial(receive_thread, fn), ())
                download_window.destroy()  # Close the download window after initiating the download

        # Button to start the download
        Button(download_window, text="Download", font=("Acumin Variable Concept", 13, 'bold'), bg="#f4fdfe", fg="#003366",
            command=start_download).pack(pady=10)


    def Connect():
        SERVERIP = ipInp.get()
        ADDRESS = (SERVERIP, PORT)
        client.connect(ADDRESS)
        messagebox.showinfo("Succeeded", "Connected to the server successfully.")
        _thread.start_new_thread(handle_server, ())
        


    Label(root, text="CLIENT", font=('Acumin Variable Concept', 20, 'bold'), bg="#f4fdfe", fg="#003366").place(x=20, y=20)
    Label(root, text="Server's IP address", font=('Acumin Variable Concept', 13), bg="#f4fdfe").place(x=20, y=70)
    ipInp = Entry(root, width=14, fg="black", border=2, bg='white', font=('arial', 20))
    ipInp.place(x=20, y=100)
    # Label(root, text="File name", font=('Acumin Variable Concept', 13), bg="#f4fdfe").place(x=20, y=220)

    con = Button(root, text="CONNECT", font=('Acumin Variable Concept', 15, 'bold'), bg="#f4fdfe", fg="#003366",
                 activebackground="#005BB5", activeforeground="white", command=Connect)
    con.place(x=260, y=100)

    send = Button(root, text="UPLOAD", font=('Acumin Variable Concept', 15, 'bold'), bg="#f4fdfe", fg="#003366",
                  activebackground="#005BB5", activeforeground="white", command=Upload)
    send.place(x=60, y=160)

    receive = Button(root, text="DOWNLOAD", font=('Acumin Variable Concept', 15, 'bold'), bg="#f4fdfe", fg="#003366",
                     activebackground="#005BB5", activeforeground="white", command=Download)
    receive.place(x=260, y=160)

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
main_root.geometry("300x280")
main_root.configure(bg="#f4fdfe")
main_root.resizable(False, False)

Label(main_root, text="Login", font=("Acumin Variable Concept", 20, 'bold'), bg="#f4fdfe", fg="#003366").pack(pady=10)
Label(main_root, text="Username", font=("Acumin Variable Concept", 13), bg="#f4fdfe").pack()
username_entry = Entry(main_root, width=20, bg="white", font=("arial", 15))
username_entry.pack()

Label(main_root, text="Password", font=("Acumin Variable Concept", 13), bg="#f4fdfe").pack()
password_entry = Entry(main_root, width=20, bg="white", font=("arial", 15), show="*")
password_entry.pack()

Button(main_root, text="Log in", font=("Acumin Variable Concept", 15, 'bold'), bg="#f4fdfe", fg="#003366", command=login).pack(pady=10)
Button(main_root, text="Sign up", font=("Acumin Variable Concept", 15, 'bold'), bg="#f4fdfe", fg="#003366", command=register).pack(pady=10)

main_root.mainloop()

from tkinter import *
import socket
from tkinter import filedialog
from tkinter import messagebox
import os
import threading
import _thread
from functools import partial

FILESIZE = 40960000
WINDOWSIZESTRING = "450x350+500+200"

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

        if not username_info or not password_info:
            messagebox.showerror("Lỗi", "Tên đăng nhập và mật khẩu không được để trống")
            return

        with open("accounts.txt", "r") as file:
            accounts = file.readlines()
            for account in accounts:
                stored_username, _ = account.strip().split(":")
                if stored_username == username_info:
                    messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại")
                    return

        with open("accounts.txt", "a") as file:
            file.write(f"{username_info}:{password_info}\n")
        
        messagebox.showinfo("Thành công", "Đăng ký thành công! Vui lòng đăng nhập.")
        register_window.destroy()

    # Cửa sổ đăng ký
    register_window = Toplevel(main_root)
    register_window.title("Register")
    register_window.geometry("300x250")
    register_window.configure(bg="#f4fdfe")
    register_window.resizable(False, False)

    Label(register_window, text="Đăng ký", font=("Acumin Variable Concept", 20, 'bold'), bg="#f4fdfe", fg="#003366").pack(pady=10)
    Label(register_window, text="Tên đăng nhập", font=("Acumin Variable Concept", 13), bg="#f4fdfe").pack()
    username_entry = Entry(register_window, width=20, bg="white", font=("arial", 15))
    username_entry.pack()

    Label(register_window, text="Mật khẩu", font=("Acumin Variable Concept", 13), bg="#f4fdfe").pack()
    password_entry = Entry(register_window, width=20, bg="white", font=("arial", 15), show="*")
    password_entry.pack()

    Button(register_window, text="Đăng ký", font=("Acumin Variable Concept", 15, 'bold'), bg="#f4fdfe", fg="#003366",
           command=register_user).pack(pady=20)

def login():
    # Hàm xử lý đăng nhập
    username_info = username_entry.get()
    password_info = password_entry.get()

    with open("accounts.txt", "r") as file:
        accounts = file.readlines()
        for account in accounts:
            stored_username, stored_password = account.strip().split(":")
            if stored_username == username_info and stored_password == password_info:
                messagebox.showinfo("Thành công", "Đăng nhập thành công!")
                open_main_window()  # Mở cửa sổ chính
                return

    messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu không chính xác")

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
    published_files = []

    # Thêm Listbox để hiển thị danh sách file đã xuất bản
    published_listbox = Listbox(root, width=40, height=10, font=('arial', 12))
    published_listbox.place(x=20, y=280)

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
                published_files.append((filedir, name))
                client.send(f"PUBLISH@{name}".encode(FORMAT))
                messagebox.showinfo("Publish", f"File '{name}' đã được xuất bản.")
                published_listbox.insert(END, name)  # Hiển thị tên file trong danh sách

    def Publish():
        select_file()

    def FindFile(filename):
        for item in published_files:
            if item[1] == filename:
                return True
        return False

    def GetFile(filename):
        ans = ("", "")
        for item in published_files:
            if item[1] == filename:
                ans = item
        return ans

    incoming_file = Entry(root, width=14, fg="black", border=2, bg='white', font=('arial', 20))
    incoming_file.place(x=20, y=250)

    def Download():
        send_msg = "DOWNLOAD@"
        fn = incoming_file.get()
        send_msg += fn
        client.send(send_msg.encode(FORMAT))
        _thread.start_new_thread(partial(receive_thread, fn), ())

    def Connect():
        SERVERIP = ipInp.get()
        ADDRESS = (SERVERIP, PORT)
        client.connect(ADDRESS)
        _thread.start_new_thread(handle_server, ())

    Label(root, text="CLIENT", font=('Acumin Variable Concept', 20, 'bold'), bg="#f4fdfe", fg="#003366").place(x=20, y=20)
    Label(root, text="Enter server's IP address", font=('Acumin Variable Concept', 13), bg="#f4fdfe").place(x=20, y=70)
    ipInp = Entry(root, width=14, fg="black", border=2, bg='white', font=('arial', 20))
    ipInp.place(x=20, y=100)
    Label(root, text="Enter file name", font=('Acumin Variable Concept', 13), bg="#f4fdfe").place(x=20, y=220)

    con = Button(root, text="CONNECT", font=('Acumin Variable Concept', 15, 'bold'), bg="#f4fdfe", fg="#003366",
                 activebackground="#005BB5", activeforeground="white", command=Connect)
    con.place(x=260, y=100)

    send = Button(root, text="PUBLISH", font=('Acumin Variable Concept', 15, 'bold'), bg="#f4fdfe", fg="#003366",
                  activebackground="#005BB5", activeforeground="white", command=Publish)
    send.place(x=160, y=160)

    receive = Button(root, text="DOWNLOAD", font=('Acumin Variable Concept', 15, 'bold'), bg="#f4fdfe", fg="#003366",
                     activebackground="#005BB5", activeforeground="white", command=Download)
    receive.place(x=260, y=250)

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
main_root.geometry("300x250")
main_root.configure(bg="#f4fdfe")
main_root.resizable(False, False)

Label(main_root, text="Đăng nhập", font=("Acumin Variable Concept", 20, 'bold'), bg="#f4fdfe", fg="#003366").pack(pady=10)
Label(main_root, text="Tên đăng nhập", font=("Acumin Variable Concept", 13), bg="#f4fdfe").pack()
username_entry = Entry(main_root, width=20, bg="white", font=("arial", 15))
username_entry.pack()

Label(main_root, text="Mật khẩu", font=("Acumin Variable Concept", 13), bg="#f4fdfe").pack()
password_entry = Entry(main_root, width=20, bg="white", font=("arial", 15), show="*")
password_entry.pack()

Button(main_root, text="Đăng nhập", font=("Acumin Variable Concept", 15, 'bold'), bg="#f4fdfe", fg="#003366", command=login).pack(pady=10)
Button(main_root, text="Đăng ký", font=("Acumin Variable Concept", 15, 'bold'), bg="#f4fdfe", fg="#003366", command=register).pack(pady=10)

main_root.mainloop()

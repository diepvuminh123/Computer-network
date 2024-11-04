from tkinter import *
from tkinter import filedialog 
from tkinter import messagebox 
from tkinter import scrolledtext 
import os
import threading
import _thread
import socket
from functools import partial

FILESIZE = 40960000
WINDOWSIZESTRING = "450x560+500+200"
root = Tk()
root.title("FILE TRANSFER SERVER")
root.geometry(WINDOWSIZESTRING)
root.configure(bg= "#FFFFF0")
root.resizable(False,False)
image_icon=PhotoImage(file="Image/app_icon.png")
root.iconphoto(False,image_icon)

Label(root, text="Server",font = ('Acumin Variable Concept',20,'bold'),bg="#FFFFF0", fg="#800020").place(x=20,y=30)
Frame(root, width=400,height=2,bg="#f3f5f6").place(x=20,y=200)
box=scrolledtext.ScrolledText(root,width=49,height=16)
box.place(x=20, y=200)

IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDR = (IP, PORT)
SIZE = 40960000
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"

server = None  # Khởi tạo server ở mức toàn cục
connlist = []
addrlist = []

def handle_client(conn, addr):
    connlist.append((conn,[])) 
    addrlist.append(addr) 
    res = f"[NEW CONNECTION] {addr} connected.\n"
    conn.send("OK@Welcome to the File Server!".encode(FORMAT))
    print(res)
    box.insert(INSERT, res)
    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]
        if cmd == "MESSAGE":
            message = f"[MESSAGE] {conn.getpeername()} {data[1]}"
            box.insert(INSERT, message)
            print(message)
        elif cmd == "UPLOAD":
            filename = data[1]
            if filename == "":
                continue
            for c in connlist:
                if c[0] == conn:
                    c[1].append(filename)
        elif cmd == "DOWNLOAD":
            msg = data[1]
            peer = conn.getpeername()[0]
            port = conn.getpeername()[1]
            filename = msg
            for c in connlist:
                if c[0] != conn:
                    send_msg = f"DOWNLOAD@{filename};{peer};{port}"
                    print(send_msg)
                    c[0].send(send_msg.encode(FORMAT))
        elif cmd == "LOGOUT":
            connlist.remove((conn, []))
            addrlist.remove(addr)
            refresh_client_list()  # Làm mới danh sách client sau khi logout
            conn.close()
            break 
    print(f"[DISCONNECTED] {addr} disconnected")
    conn.close()

def refresh_client_list():
    """Hàm làm mới danh sách client hiển thị trên box."""
    box.delete('1.0', END)  # Xóa nội dung hiện tại
    box.insert(INSERT, "[CLIENT LIST]\n")
    for addr in addrlist:
        box.insert(END, f"Client: {addr}\n")

def printList(list, show):
    for elem in list:
        show.insert(END, "Client:", f"{elem[0]}:{elem[1]}")

def is_valid_input(input):
    try:
        ip, port = input.split(":")
        return True
    except:
        return False

def Ping(ip_var):
    input = ip_var.get()
    if input == "":
        messagebox.showinfo("Warning", "Fields cannot be empty")
    else:
        if is_valid_input(input):
            ip, port = input.split(':')
            result = False
            for addr in addrlist:
                if ip == addr[0] and port == str(addr[1]):
                    result = True
                    print("Address is valid")
                    messagebox.showinfo("ACTIVED", "This client is currently connected")
                    return
            if not result:
                messagebox.showinfo("Warning", "Address is not valid")          
        else:
            messagebox.showerror("ERROR", "Syntax error")

def ClientList():
    window=Toplevel(root)
    window.title("CLIENT STATUS")
    window.geometry(WINDOWSIZESTRING)
    window.configure(bg="#FFFFF0")
    window.resizable(False,False)
    Label(window, text="The connected clients' list",font = ('Acumin Variable Concept',20,'bold'),bg="#FFFFF0", fg="#800020").place(x=20,y=30)
    Frame(window, width=400,height=2,bg="#f3f5f6").place(x=20,y=200)
    show_clientList = Listbox(window,width=100,height=50)
    show_clientList.place(x = 0, y = 210)
    printList(addrlist, show_clientList)
    
    dis_ip_var = StringVar()
    ping_ip_var = StringVar()
    
    discover_label = Label(window, text="Enter IP:PORT to discover").place(x=210, y=100)
    discover_ip = Entry(window, textvariable=dis_ip_var, width=30, bd=4).place(x=210, y=120)
    discover = Button(window, text="Discover", font=('Acumin Variable Concept',17,'bold'), bg="#FFFFF0", width=10, height=1, command=lambda: Discover(dis_ip_var))
    discover.place(x=50, y=100)
    
    ping_label = Label(window, text="Enter IP:PORT to ping").place(x=210, y=150)
    ping_ip = Entry(window, textvariable=ping_ip_var, width=30, bd=4).place(x=210, y=170)
    ping = Button(window, text="Ping", font=('Acumin Variable Concept',17,'bold'), bg="#FFFFF0", width=10, height=1, command=lambda: Ping(ping_ip_var))
    ping.place(x=50, y=150)
    
    def Discover(ip_var):
        input = ip_var.get()
        if input == "":
            messagebox.showinfo("Warning", "Fields cannot be empty")
        else:
            if is_valid_input(input):
                ip, port = input.split(':')
                result = False
                for c in connlist:
                    pe = c[0].getpeername()[0]
                    po = c[0].getpeername()[1]
                    if ip == pe and port == str(po):
                        result = True
                        wd = Toplevel(window)
                        wd.title("DISCOVER")
                        wd.geometry(WINDOWSIZESTRING)
                        wd.configure(bg="#FFFFF0")
                        wd.resizable(False, False)
                        Label(wd, text="List of sharing files", font=('Acumin Variable Concept',20,'bold'), bg="#FFFFF0").place(x=20, y=30)
                        show_fileList = Listbox(wd, width=100, height=50)
                        show_fileList.place(x=0, y=100)
                        for f in c[1]:
                            show_fileList.insert(END, f)
                        wd.mainloop()
                        return
                if not result:
                    messagebox.showinfo("Warning", "Address is not valid")
            else:
                messagebox.showerror("ERROR", "Syntax error")
    window.mainloop()

def Server():
    global server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    res = f"[STARTING] Server is starting\n[LISTENING] Server is listening on {IP}:{PORT}.\nWaiting for connection...\n"
    box.insert(INSERT, res)

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        msg = f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}\n"
        box.insert(INSERT, msg)
        print(msg)

def ServerThread():
    _thread.start_new_thread(Server, ())
    start_button.place_forget()
    stop_button.place(x=50, y=100)

def StopServer():
    global server
    if server:
        for conn, _ in connlist:
            conn.close()  # Đóng tất cả các kết nối của client
        server.close()  # Đóng server
        server = None   # Đặt lại server về None để có thể khởi động lại
        connlist.clear()  # Xóa danh sách client
        addrlist.clear()
        box.insert(INSERT, "[STOPPED] Server has stopped.\n")
    stop_button.place_forget()
    start_button.place(x=50, y=100)

def startClientList():
    _thread.start_new_thread(ClientList, ())

# Nút START SERVER
start_button = Button(root, text="START SERVER", font=('Acumin Variable Concept', 17, 'bold'),
                      bg="#FFFFF0", fg="#800020", activebackground="#005BB5", activeforeground="white", 
                      command=ServerThread)
start_button.place(x=50, y=100)

# Nút STOP SERVER (ẩn ban đầu)
stop_button = Button(root, text="STOP SERVER", font=('Acumin Variable Concept', 17, 'bold'),
                     bg="#FFFFF0", fg="#cc0000", activebackground="#B50000", activeforeground="white", 
                     command=StopServer)

# Nút CLIENT LIST
clist_button = Button(root, text="CLIENT LIST", font=('Acumin Variable Concept', 17, 'bold'),
                      bg="#FFFFF0", fg="#800020", activebackground="#005BB5", activeforeground="white", 
                      command=startClientList)
clist_button.place(x=250, y=100)

root.mainloop()

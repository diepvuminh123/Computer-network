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
WINDOWSIZESTRING = "450x530+500+200"
root = Tk()
root.title("FILE TRANSFER TRACKER")
root.geometry(WINDOWSIZESTRING)
root.configure(bg= "#FFFFF0")
root.resizable(False,False)
image_icon=PhotoImage(file="Image/app_icon.png")
root.iconphoto(False,image_icon)

# Label(root, text="Server",font = ('Segoe UI',20,'bold'),bg="#FFFFF0", fg="#800020").place(x=20,y=30)
Frame(root, width=400,height=2,bg="#f3f5f6").place(x=20,y=200)
box=scrolledtext.ScrolledText(root,width=56, height=26)
box.place(x=20, y=170)

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
    connlist.append((conn, []))  # Add client with empty file list
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
            # Add uploaded file to client's file list
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
            # Remove client files and address from the lists
            for c in connlist:
                if c[0] == conn:
                    connlist.remove(c)  # Remove the client's connection and files
                    break
            addrlist.remove(addr)
            refresh_client_list()  # Refresh client list in the display
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
                messagebox.showinfo("DEACTIVATED", "This client is currently NOT connected")          
        else:
            messagebox.showerror("ERROR", "Syntax error")

def ClientList():
    window=Toplevel(root)
    window.title("CLIENT STATUS")
    window.geometry("450x480+500+200")
    window.configure(bg="#FFFFF0")
    window.resizable(False,False)
    # Label(window, text="The connected clients' list",font = ('Segoe UI',20,'bold'),bg="#FFFFF0", fg="#800020").place(x=20,y=30)
    Frame(window, width=400,height=2,bg="#f3f5f6").place(x=20,y=200)
    show_clientList = Listbox(window,width=68,height=18)
    show_clientList.place(x = 20, y = 170)
    printList(addrlist, show_clientList)
    
    dis_ip_var = StringVar()
    ping_ip_var = StringVar()
    
    # ping_label = Label(window, text="Enter IP:PORT to ping").place(x=210, y=150)
    ping_ip = Entry(window, textvariable=ping_ip_var, width=15, bd=4, font=('Arial', 14) ).place(x=240, y=31)
    ping = Button(window, text="Ping", font=('Segoe UI',17,'bold'), fg="#800020", bg="#FFFFF0", width=10, height=1, command=lambda: Ping(ping_ip_var))
    ping.place(x=50, y=20)

    # discover_label = Label(window, text="Enter IP:PORT to discover").place(x=210, y=100)
    discover_ip = Entry(window, textvariable=dis_ip_var, width=15, bd=4, font=('Arial', 14)).place(x=240, y=102)
    discover = Button(window, text="Detail", font=('Segoe UI',17,'bold'), fg="#800020", bg="#FFFFF0", width=10, height=1, command=lambda: Discover(dis_ip_var))
    discover.place(x=50, y=90)
    
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
                        wd.geometry("450x410+500+200")
                        wd.configure(bg="#FFFFF0")
                        wd.resizable(False, False)
                        Label(wd, text="Shared files", font=('Segoe UI',20,'bold'), fg="#800020", bg="#FFFFF0").place(x=155, y=30)
                        show_fileList = Listbox(wd, width=68, height=18)
                        show_fileList.place(x=20, y=100)
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
    stop_button.place(x=155, y=20)

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
    start_button.place(x=140, y=20)

def startClientList():
    _thread.start_new_thread(ClientList, ())

# Nút START SERVER
start_button = Button(root, text="START SERVER", font=('Segoe UI', 17, 'bold'),
                      bg="#FFFFF0", fg="#800020", activebackground="#005BB5", activeforeground="white", 
                      command=ServerThread)
start_button.place(x=140, y=20)

# Nút STOP SERVER (ẩn ban đầu)
stop_button = Button(root, text="STOP SERVER", font=('Segoe UI', 17, 'bold'),
                     bg="#FFFFF0", fg="#cc0000", activebackground="#B50000", activeforeground="white", 
                     command=StopServer)

# Nút CLIENT LIST
clist_button = Button(root, text="CLIENT LIST", font=('Segoe UI', 17, 'bold'),
                      bg="#FFFFF0", fg="#800020", activebackground="#005BB5", activeforeground="white", 
                      command=startClientList)
clist_button.place(x=155, y=90)

root.mainloop()

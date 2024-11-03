from tkinter import *
from tkinter import filedialog 
from tkinter import messagebox 
from tkinter import scrolledtext 
import os
import threading
import socket
import _thread
from functools import partial


FILESIZE = 40960000
WINDOWSIZESTRING = "450x560+500+200"
root = Tk()
root.title("FILE TRANSFER SERVER")
root.geometry(WINDOWSIZESTRING)
root.configure(bg= "#f4fdfe")
root.resizable(False,False)
image_icon=PhotoImage(file="Image/app_icon.png")
root.iconphoto(False,image_icon)


Label(root, text="Server",font = ('Acumin Variable Concept',20,'bold'),bg="#f4fdfe", fg="#003366").place(x=20,y=30)
Frame(root, width=400,height=2,bg="#f3f5f6").place(x=20,y=200)
box=scrolledtext.ScrolledText(root,width=49,height=16)
box.place(x=20, y=200)


IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDR = (IP, PORT)
SIZE = 40960000
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"


server = None
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
        elif cmd == "PUBLISH":
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
            connlist.remove(conn)
            addrlist.remove(addr)
            break
    print(f"[DISCONNECTED] {addr} disconnected")
    conn.close()

def start_server():
    global server
    res = "[STARTING] Server is starting\n"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    res += f"[LISTENING] Server is listening on {IP}:{PORT}.\nWaiting for connection...\n"
    box.insert(INSERT, res)
    start_button.place_forget()
    stop_button.place(x=50, y=100)

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        msg = f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}\n"
        box.insert(INSERT, msg)
        print(msg)


def stop_server():
    global server
    if server:
        for conn, _ in connlist:
            conn.close()  # Đóng kết nối của từng client
        server.close()
        server = None
        connlist.clear()  # Xóa danh sách client
        addrlist.clear()
        box.insert(INSERT, "[STOPPED] Server has stopped.\n")
    stop_button.place_forget()
    start_button.place(x=50, y=100)


def server_thread():
    _thread.start_new_thread(start_server, ())


def startClientList():
    _thread.start_new_thread(ClientList, ())


start_button = Button(
    root,
    text="START SERVER",
    font=('Acumin Variable Concept', 17, 'bold'),
    bg="#f4fdfe",
    fg="#003366",
    activebackground="#005BB5",
    activeforeground="white",
    command=server_thread
)
start_button.place(x=50, y=100)

stop_button = Button(
    root,
    text="STOP SERVER",
    font=('Acumin Variable Concept', 17, 'bold'),
    bg="#f4fdfe",
    fg="#003366",
    activebackground="#B50000",
    activeforeground="white",
    command=stop_server
)

clist_button = Button(
    root,
    text="CLIENT LIST",
    font=('Acumin Variable Concept', 17, 'bold'),
    bg="#f4fdfe",
    fg="#003366",
    activebackground="#005BB5",
    activeforeground="white",
    command=startClientList
)
clist_button.place(x=250, y=100)

root.mainloop()

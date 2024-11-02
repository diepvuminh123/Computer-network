from tkinter import *
import socket
from tkinter import filedialog 
from tkinter import messagebox 
import os
import threading
import _thread
from functools import partial
import sys


FILESIZE = 40960000
WINDOWSIZESTRING = "450x350+500+200"

root = Tk()
root.title("FILE TRANSFER CLIENT")
root.geometry(WINDOWSIZESTRING)
root.configure(bg= "#f4fdfe")
root.resizable(False,False)

image_icon=PhotoImage(file="Image/app_icon.png")
root.iconphoto(False,image_icon)

loggedin = False

IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
DLPORT = 4444
ADDR = (IP, PORT)
SIZE = 40960000
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

published_files = [] 

def receive_thread(filename):
    host_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host_client.bind((IP,DLPORT))
    host_client.listen()
    while True:
        friend, addr = host_client.accept()
        print(f"Peer connected: {addr}\n")
        f = open("downloads/"+filename,"wb")
        l = friend.recv(SIZE)
        while True:
            while (l):
                f.write(l)
                l = friend.recv(SIZE)
            f.close()
            break
        friend.close()
        break
    host_client.close()



def share_thread(peer,port,file):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("peer",peer,"port",port)
    client_socket.connect((peer,DLPORT))
    print(file)
    f = open(file[0], 'rb')
    l = f.read(SIZE)
    while (l):
        client_socket.send(l)
        l = f.read(SIZE)
    f.close()
    client_socket.close()




def PrintAllLocal():
    for item in published_files:
        print(item)
        print(item[1])



def select_file():
    filedir=filedialog.askopenfilename(initialdir=os.getcwd(),title='Select Image File',filetype=(('file_type','*.txt'),('all files','*.*')))
    if (filedir!=None):
        name = os.path.basename(filedir)
        if (name!=""):
            print('Published', name)
        
        published_files.append((filedir,name))
        client.send(f"PUBLISH@{name}".encode(FORMAT))
    
def Publish():
    select_file()
    




def FindFile(filename):
    for (item) in published_files:
        cpr = item[1]
        if (cpr==filename):
            return True
    print("COULD NOT FIND")
    return False

def GetFile(filename):
    ans = ("","")
    for item in published_files:
        cpr = item[1]
        if (item[1]==filename):
            ans = item
    print(ans)
    return ans

def HelpDiscover():
    danhsach = []
    for item in published_files:
        danhsach.append(item[1])
    return danhsach

incoming_file = Entry(root, width=14, fg="black", border=2, bg='white', font=('arial', 20))
incoming_file.place(x=20, y=250)

def Download():
 
    send_msg = "DOWNLOAD@"
    fn = incoming_file.get()
    send_msg += fn
 
    client.send(send_msg.encode(FORMAT))
    _thread.start_new_thread(partial(receive_thread,fn), ())





def Connect():
    SERVERIP = ipInp.get()
    ADDRESS = (SERVERIP,PORT)
    client.connect(ADDRESS)
    loggedin = True
    _thread.start_new_thread(handle_server, ())




Label(root, text="Client",font = ('Acumin Variable Concept',20,'bold'),bg="#f4fdfe").place(x=20,y=20)



Label(root, text="Enter server's IP address", font= ('Acumin Variable Concept',13),bg="#f4fdfe").place(x=20,y=70)
ipInp = Entry(root, width=14, fg="black", border=2, bg='white', font=('arial', 20))
ipInp.place(x=20, y=100)
Frame(root, width=400,height=2,bg="#f3f5f6").place(x=25,y=60)
Label(root, text="Enter file name", font= ('Acumin Variable Concept',13),bg="#f4fdfe").place(x=20,y=220)


con=Button(root,text="CONNECT",font=('Acumin Variable Concept',15,'bold'),bg="#f4fdfe",command=Connect)
con.place(x=260,y=100)
send=Button(root,text="PUBLISH",font=('Acumin Variable Concept',15,'bold'),bg="#f4fdfe",command=Publish)
send.place(x=160,y=160)
receive=Button(root,text="DOWNLOAD",font=('Acumin Variable Concept',15,'bold'),bg="#f4fdfe",command=Download)
receive.place(x=260,y=250)



def handle_server():
    while (True):
  
        data = client.recv(SIZE).decode(FORMAT)
        temp = data.split("@")
        cmd = temp[0]
        if (len(temp)>1):
            msg = temp[1]

        if cmd == "DISCONNECTED":
            print(f"[SERVER]: {msg}")
            break
        elif cmd == "OK":
            print(f"{msg}")
        elif cmd == "DOWNLOAD":
            file, peer, portstr = msg.split(";")
            port = int(portstr)
            print(f"[PEER]: Request download: {file} from {peer}, port {portstr}")
            find = FindFile(file)
            if (find==True):
                print("Found")
                get = GetFile(file)
                _thread.start_new_thread(partial(share_thread, peer,port,get), ())
                




def Logout():
    if (loggedin==True):
        client.send("MESSAGE@Disconnected\n".encode(FORMAT))
    exit()

root.protocol("WM_DELETE_WINDOW", Logout)

root.mainloop()



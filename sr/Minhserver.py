#server.py 

import socket 

host = 'localhost'
port = 4000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))

s.listen(5) 
print("Server listening on port", port)

c, addr = s.accept()
print("Connect from ", str(addr))
#Test
c.send(b"Hello, how are you")
c.send("Bye".encode())
c.close()
s.close()


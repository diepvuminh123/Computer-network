import socket

# Tracker connection info
tracker_host = 'localhost'
tracker_port = 4000

# Client-specific information
info_hash = 'file123hash'  # Unique identifier for the file the client wants to share or download
peer_id = 'peer1'           # Unique identifier for this peer
client_port = 5001          # Port this client listens on for peer-to-peer connections

def connect_to_tracker():
    try:
        # Create a socket to connect to the tracker
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect to the tracker
        client_socket.connect((tracker_host, tracker_port))
        print("Connected to tracker")

        # Send info_hash, peer_id, and client_port as a comma-separated string
        message = f"{info_hash},{peer_id},{client_port}"
        client_socket.sendall(message.encode())

        # Receive confirmation from the tracker
        response = client_socket.recv(1024).decode()
        print("Tracker response:", response)
        
    except Exception as e:
        print("Error connecting to tracker:", e)
    finally:
        client_socket.close()

# Run the client
connect_to_tracker()

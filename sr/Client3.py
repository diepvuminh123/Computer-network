import socket

# Tracker connection info
tracker_host = 'localhost'
tracker_port = 4000

# Client-specific information
info_hash = 'file789hash'  # Unique identifier for the file the client wants to share or download
peer_id = 'peer3'           # Unique identifier for this peer
client_ip = 'localhost'     # IP address of this client
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
        
        # Request the list of peers from the tracker
        client_socket.sendall(b"REQUEST")
        peer_list_raw = client_socket.recv(4096).decode()  # Use larger buffer if needed
        print("Original Peer List:")
        print(peer_list_raw)
        
        # Process and filter the peer list to exclude self
        filtered_peer_list = []
        skip_section = False
        for line in peer_list_raw.splitlines():
            # Check if the line is the start of a new file section
            if line.startswith("File"):
                # Determine if this section matches Client3's info_hash
                if info_hash in line:
                    skip_section = True  # Skip this section entirely
                else:
                    skip_section = False
                    filtered_peer_list.append(line)  # Keep the heading for other files
            elif not skip_section:
                filtered_peer_list.append(line)  # Add peer details for other files

        print("\nFiltered Peer List (excluding self):")
        for line in filtered_peer_list:
            print(line)
        
    except Exception as e:
        print("Error connecting to tracker:", e)
    finally:
        client_socket.close()

# Run the client
connect_to_tracker()

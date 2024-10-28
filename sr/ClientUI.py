# cli.py
import threading
from node import start_node
from peer import run_peer_server

def start_cli():
    file_hash = input("Enter file hash to share or download: ")
    # Start peer server to upload the file if others request
    threading.Thread(target=run_peer_server, args=(9000, file_hash)).start()
    # Start download from other peers
    start_node(file_hash)

if __name__ == "__main__":
    start_cli()

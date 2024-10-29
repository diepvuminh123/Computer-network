# Link report
https://www.overleaf.com/7514497376jzgchqwcnfss#726c2a
# Centralized File Sharing System

## Project Overview
This project involves the development of a network application based on the TCP/IP protocol. The system emulates a basic torrent network with two key components:  
- **Tracker (Server):** Manages the list of connected nodes and tracks the files they host.  
- **Node (Client):** Participates in uploading and downloading files to/from other nodes.

The system supports **Multi-Dimensional Data Transmission (MDDT)**, allowing simultaneous downloads from multiple peers to optimize performance.  

## Objectives
- Facilitate seamless file sharing between multiple computers (nodes) connected to a central server (tracker).
- Improve the management and accessibility of files shared in the network.

## Key Features
1. **Tracker (Server)**  
   - Stores information about files and tracks the status of downloads.
   - Responds to node requests by providing peer information for downloads.
   
2. **Node (Client)**  
   - Communicates with the tracker to register files and request peers.
   - Supports multi-threaded downloads and peer-to-peer (P2P) communication.
   - Implements strategies like “Rarest First” to optimize downloads.

3. **Communication Protocols**  
   - **Tracker-to-Node:** Exchanges file and peer information.
   - **Peer-to-Peer:** Nodes connect directly to share files without needing the tracker.  
   - **MDDT:** Uses multi-threading to maximize download efficiency.

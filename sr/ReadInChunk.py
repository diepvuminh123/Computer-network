import os
import hashlib

def read_file_in_chunks(file_path, chunk_size=1024):
    """
    Reads a file in chunks, calculates a hash for each chunk, and stores
    each piece in a list. The original file remains unaltered.
    """
    file_name = os.path.basename(file_path)
    file_pieces = []
    with open(file_path, 'rb') as f:
        piece_num = 0
        while chunk := f.read(chunk_size):
            # Calculate the hash for the current chunk (for verification)
            piece_hash = hashlib.sha1(chunk).hexdigest()
            # Append the piece information as a dictionary
            file_pieces.append({
                'file_name': file_name,
                'piece_num': piece_num,
                'content': chunk,  # This is the actual chunk of data
                'hash': piece_hash  # Hash for integrity check
            })
            piece_num += 1
    return file_pieces

# Example usage
file_path = 'E:\\pdf\\prob-Danger Detection.pdf'
pieces = read_file_in_chunks(file_path, chunk_size=1024)

# Display information about each piece
for piece in pieces:
    print(f"Piece {piece['piece_num']}: Hash = {piece['hash']}, Size = {len(piece['content'])} bytes")

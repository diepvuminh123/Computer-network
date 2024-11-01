import os
import hashlib

def read_file_in_chunks(file_path, output_dir, chunk_size=1024):
    """
    Reads a file in chunks, calculates a hash for each chunk, and saves
    each piece in the specified output directory.
    """
    file_name = os.path.basename(file_path)
    os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists
    
    with open(file_path, 'rb') as f:
        piece_num = 0
        while chunk := f.read(chunk_size):
            # Calculate the hash for the current chunk (for verification)
            piece_hash = hashlib.sha1(chunk).hexdigest()
            # Define the output path for each chunk
            part_path = os.path.join(output_dir, f"{file_name}_part_{piece_num}")
            
            # Write the chunk to a file in the output directory
            with open(part_path, 'wb') as part_file:
                part_file.write(chunk)
            
            print(f"Saved piece {piece_num} as {part_path} with hash {piece_hash}")
            piece_num += 1

# Example usage
file_path = 'E:\\pdf\\prob-Danger Detection.pdf'
output_dir = 'E:\\New folder\\Computer-network\\sr2\\shared_files'
read_file_in_chunks(file_path, output_dir=output_dir, chunk_size=1024)

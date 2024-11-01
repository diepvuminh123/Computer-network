import os

def assemble_file_from_chunks(output_file_path, input_dir="shared_files"):
    """
    Assembles all file pieces in the specified input directory into a single file.
    Assumes pieces are named with the format `{original_filename}_part_{piece_num}`.
    Deletes each piece after it has been added to the final file.
    """
    # Extract base filename from the output path to match piece names
    base_name = os.path.basename(output_file_path)
    # Collect all matching pieces and sort by piece number
    piece_files = sorted(
        [f for f in os.listdir(input_dir) if f.startswith(base_name) and "_part_" in f],
        key=lambda x: int(x.split("_part_")[-1])
    )

    if not piece_files:
        print("No file pieces found in the specified directory.")
        return

    # Open the output file in write-binary mode
    with open(output_file_path, 'wb') as output_file:
        for piece_file in piece_files:
            piece_path = os.path.join(input_dir, piece_file)
            try:
                with open(piece_path, 'rb') as piece:
                    chunk_data = piece.read()
                    if chunk_data:  # Ensure there's data in the chunk
                        output_file.write(chunk_data)
                        print(f"Added {piece_file} to {output_file_path}")
                    else:
                        print(f"Warning: {piece_file} is empty.")
                # Delete the piece after writing it to the output file
                os.remove(piece_path)
                print(f"Deleted {piece_file}")
            except Exception as e:
                print(f"Error reading or writing {piece_file}: {e}")

    print(f"File assembled successfully as {output_file_path}")

# Example usage
output_file_path = 'E:\\New folder\\Computer-network\\sr2\\downloaded_files\\reconstructed_file.pdf'
input_dir = 'E:\\New folder\\Computer-network\\sr2\\shared_files'
assemble_file_from_chunks(output_file_path, input_dir=input_dir)

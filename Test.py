import hashlib
import bencodepy

def process_file(file_path, chunk_size):
    file_chunks = []
    chunk_hashes = []

    with open(file_path, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            file_chunks.append(chunk)

            # Tính mã băm SHA-1 cho từng phần
            sha1_hash = hashlib.sha1(chunk).hexdigest()
            chunk_hashes.append(sha1_hash)

    # Tạo tệp .torrent
    file_name = file_path.split('/')[-1]  # Lấy tên tệp từ đường dẫn
    file_size = sum(len(chunk) for chunk in file_chunks)  # Tính kích thước tệp gốc

    metadata = {
        'info': {
            'file_name': file_name,
            'file_size': file_size,
            'chunks': [{'chunk_number': i + 1, 'chunk_hash': chunk_hash} for i, chunk_hash in enumerate(chunk_hashes)]
        }
    }

    # Ghi tệp .torrent
    with open(file_name + '.torrent', 'wb') as torrent_file:
        torrent_file.write(bencodepy.encode(metadata))

    return file_chunks, chunk_hashes

# Sử dụng hàm
file_path = 'C:\\Users\\ADMIN\\Desktop\\Computer-network\\AAA.pdf'  # Thay đổi đường dẫn tới tệp của bạn
chunk_size = 1024 * 1024  # Kích thước từng phần, ví dụ 1 MB
file_chunks, chunk_hashes = process_file(file_path, chunk_size)

import hashlib
import bencodepy

def download_and_save(file_path):
    # Đọc tệp .torrent để lấy metadata
    with open(file_path, 'rb') as torrent_file:
        torrent_data = bencodepy.decode(torrent_file.read())

    # Lấy thông tin từ metadata
    info = torrent_data[b'info']
    file_name = info[b'file_name'].decode('utf-8')  # Giải mã tên tệp
    chunks = info[b'chunks']

    # Giả lập quá trình tải xuống và lưu vào tệp
    for chunk in chunks:
        chunk_number = chunk[b'chunk_number']
        chunk_hash = chunk[b'chunk_hash'].decode('utf-8')  # Giải mã mã băm

        # Tạo nội dung ngẫu nhiên cho từng phần (mô phỏng dữ liệu tải về)
        chunk_size = 1024 * 1024  # Kích thước phần (ví dụ: 1 MB)
        chunk_data = bytearray(chunk_size)  # Tạo một phần dữ liệu trống

        # Lưu phần vào tệp
        with open(f'downloaded_chunk_{chunk_number}.bin', 'wb') as file:
            file.write(chunk_data)

        # Xác minh mã băm
        sha1_hash = hashlib.sha1(chunk_data).hexdigest()
        if sha1_hash == chunk_hash:
            print(f'Chunk {chunk_number} downloaded and verified successfully.')
        else:
            print(f'Chunk {chunk_number} verification failed.')

# Sử dụng hàm để tải xuống từ tệp .torrent
torrent_file_path = 'C:\\Users\\ADMIN\\Desktop\\Computer-network\\AAA.torrent'  # Thay đổi đường dẫn tới tệp .torrent của bạn
download_and_save(torrent_file_path)

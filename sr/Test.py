import hashlib

def create_magnet_link(file_path, tracker_url):
    # Đọc file để tạo mã băm SHA-1 cho magnet link
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
            file_hash = hashlib.sha1(file_data).hexdigest()
    except FileNotFoundError:
        print("Không tìm thấy file. Vui lòng kiểm tra lại đường dẫn.")
        return None

    # Lấy tên file từ đường dẫn
    file_name = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]

    # Tạo link magnet
    magnet_link = f"magnet:?xt=urn:btih:{file_hash}&dn={file_name}&tr={tracker_url}"
    return magnet_link

# Yêu cầu người dùng nhập đường dẫn tệp và URL của tracker
file_path = input("Nhập đường dẫn file: ")
tracker_url = input("Nhập URL của tracker (vd: http://tracker.example.com/announce): ")

# Tạo link magnet và hiển thị
magnet_link = create_magnet_link(file_path, tracker_url)
if magnet_link:
    print("Link magnet của bạn là:", magnet_link)

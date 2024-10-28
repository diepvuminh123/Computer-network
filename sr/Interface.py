# interface.py

import Node

def main():
    print("Chào mừng đến với ứng dụng chia sẻ file P2P!")
    print("1. Chia sẻ một tệp")
    print("2. Tải tệp từ mạng")
    print("3. Ghép tệp đã tải")
    choice = input("Lựa chọn của bạn (1, 2 hoặc 3): ")
    
    if choice == "1":
        file_path = input("Nhập đường dẫn tới tệp bạn muốn chia sẻ: ")
        parts = Node.split_file(file_path)
        for file_name, part_num in parts:
            Node.register_piece_with_tracker(file_name, part_num)
        print("Tệp đã được chia sẻ thành công!")

    elif choice == "2":
        file_name = input("Nhập tên tệp bạn muốn tải: ")
        total_parts = int(input("Nhập số phần của tệp: "))
        
        for part_num in range(total_parts):
            peers = Node.get_peers_for_piece(file_name, part_num)
            if peers:
                for peer in peers:
                    peer_ip, peer_port = peer
                    Node.download_piece_from_peer(peer_ip, peer_port, file_name, part_num)
        print("Tải tệp hoàn tất!")

    elif choice == "3":
        file_name = input("Nhập tên tệp bạn muốn ghép: ")
        total_parts = int(input("Nhập số phần của tệp: "))
        success = Node.assemble_file(file_name, total_parts)
        if success:
            print("Tệp đã được ghép thành công!")
        else:
            print("Có lỗi khi ghép tệp. Kiểm tra lại các phần đã tải xuống.")
        
if __name__ == "__main__":
    main()

# ROP Chain cho Casio fx-580VN X - Phiên bản đã sửa lỗi cuối cùng
#
# Chức năng:
#  - Hiển thị "hello" khi nhấn phím '1' và "world" khi nhấn phím '2'.
#  - Đã sửa lỗi logic về pop gadget. Mã nguồn được sao lưu và khôi phục
#    một cách an toàn để đảm bảo sự ổn định.

org 0xd730

home:
    # Khởi tạo môi trường
    setlr         # Đặt thanh ghi link
    setsfr        # Thiết lập thanh ghi chức năng đặc biệt
    buffer_clear  # Xóa bộ đệm màn hình
    
    # Bước sao lưu ban đầu (chỉ thực hiện một lần)
    # Sao chép mã nguồn từ 'home' (er2) đến địa chỉ backup 0xd830 (er0).
    xr0 = adr_of home, 0xe9e0
    BL memcpy,pop er0
    0x0101 # Chiều dài của dữ liệu cần sao chép, được pop vào er0 sau khi memcpy

loop:
    # Vòng lặp chính, chờ phím bấm và xử lý
    setlr
    di,rt

    # Lấy mã phím (r0) và chuyển nó vào er0 một cách an toàn
    er0 = 0xd630      # Đặt địa chỉ tạm vào er0
    getkeycode
    er0=[er0],pop xr8,rt # Gadget: Lấy giá trị từ địa chỉ tạm vào er0
    0x3030303030303030 # Dữ liệu pop

    # Chuẩn bị stack để nhảy đến routine kiểm tra phím
    er14 = adr_of [-2] key_check
    sp = er14, pop er14

key_check:
    # Gadget để kiểm tra phím '1'
    er2 = 0x01, 0x01
    er0 - er2_eq,r0 = 1,rt
    er4 = adr_of [-2] check_key_2
    er2 = adr_arith [-2] print_hello - adr_arith [-2] check_key_2, 0x00
    er0*=r2,er2=er0,er0+=er4,rt
    er6 = er0,er0 = er8,pop qr8
    0x3030303030303030
    sp = er6, pop er8

check_key_2:
    # Gadget để kiểm tra phím '2'
    er2 = 0x01, 0x02
    er0 - er2_eq,r0 = 1,rt
    er4 = adr_of [-2] restore_and_loop
    er2 = adr_arith [-2] print_world - adr_arith [-2] restore_and_loop, 0x00
    er0*=r2,er2=er0,er0+=er4,rt
    er6 = er0,er0 = er8,pop qr8
    0x3030303030303030
    sp = er6, pop er8
    
restore_and_loop:
    # Routine khôi phục mã nguồn và quay lại vòng lặp
    setlr
    
    # SỬA LỖI: Gán lại địa chỉ đích vào er0 trước khi gọi memcpy
    # Do 'pop er0' trước đó đã ghi đè er0.
    er0 = adr_of home
    er2 = 0xe9e0
    BL memcpy,pop er0
    0x0101 # Chiều dài của dữ liệu

    # Quay lại vòng lặp chính
    goto loop
    
print_hello:
    # Routine hiển thị "hello"
    setlr
    buffer_clear
    xr0 = 0x0008d137
    [er0]=r2
    xr0 = 0x0000, adr_of [-2] text_hello
    smallprint
    goto restore_and_loop

print_world:
    # Routine hiển thị "world"
    setlr
    buffer_clear
    xr0 = 0x0008d137
    [er0]=r2
    xr0 = 0x0000, adr_of [-2] text_world
    smallprint
    goto restore_and_loop

text_hello:
    str "hello"
text_world:
    str "world"
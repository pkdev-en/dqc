org 0xd730
# hàm calc_mode hoạt động như sau:
# Địa chỉ của địa chỉ chứa formula được lưu ở er0
# Địa chỉ chứa kết quả lưu ở er2
enter:
	call 2e236
# Gọi hàm calc_mode để lưu hàm số từ D180 (input area)
	xr0 = 0xee80, 0xd180
	BL strcpy
# Đưa D180 lên EE80 (Vì có 2 hàm f(x),g(x) nên mỗi hàm một vùng địa chỉ
	call 2e236
# Gọi hàm calc_mode để lưu hàm số từ D180 (input area)
	xr0 = 0x0001d0f5
	[er0]=r2
# Đưa giá trị ở địa chỉ D0F5 thành 01,lúc này máy sẽ không bị tắt để trước khi bấm [Shift] máy vẫn luôn mở màn hình dù qua 10 phút.Chi tiết hãy đọc disas phần shutdown_func
	setlr
	setsfr
	buffer_clear
	xr0 = adr_of addr_set_x, 0xd36a
	call 17922
# Đưa x về giá trị ban đầu (-9,6)
	xr0 = 0x0008d137
	[er0]=r2
# Đưa font chữ về 08
	xr0 = adr_of [+4788] update_screen_status,adr_of [+4784] pos
	[er0]=er2,rt
# Giúp vị trí cũ và vị trí mới cập nhất cùng lúc,từ đó line_draw khi chạy ở lúc đầu hay lúc cập nhật vị trí khác nhau sẽ không bị lỗi
# Ví dụ:Vị trí cũ = 00 00, vị trí mới = 20 00 thì line_draw sẽ bị nối lệch
	xr0 = hex 61 01 11 00
	char_print
	xr0 = hex b8 18 10 00
	char_print
	xr0 = hex 58 21 30 00
	char_print
	xr0 = hex 60 40 60 00
	line_draw
	xr0 = hex 00 20 c0 20
	line_draw
	render.ddd4
# Đưa màn hình về màn hình đồ thị (Bao gồm trục,chữ x,y ...)
home:
	setlr
	xr0 = adr_of addr_input, 0xd374
	call 17922
# Giá trị y là kết quả phép tính nhập ở D180 hoặc EE80
	xr0 = adr_of addr_add_x, 0xd36a
	call 17922
# Lấy giá trị của x cộng cho x,rồi lưu lại tại x để được giá trị x mới
	xr0 = adr_of addr_int_y, 0xd32e
	call 17922
# Làm tròn giá trị y, lưu ở biến A
	xr0 = adr_of addr_int_x, 0xd338
	call 17922
# Làm tròn giá trị x, lưu ở biến B
	xr0 = adr_of addr_total, 0xd3a0
	call 17922
# Tính giá trị tổng theo công thức, lưu ở D3A0
	xr0 = 0x0018ddd4
	memzero
# Xoá status bar trong trường hợp pixel ở status bar
check_range:
	er2 = 0xd3a8
	setlr
	er0=[er2],r2 = 9,rt
	r1 = 0,rt
	er2 = 0x0003
	call 0c790
	er2 = adr_arith check_error - adr_arith goto_draw_skip,0x00
	er4 = adr_of [-2] goto_draw_skip
	er0*=r2,er2 = er0,er0+=er4,rt
	er14 = er0,pop xr0
	0x30303030
	sp = er14,pop er14
# CMP phạm vi màn hình thông qua tổng (D3A0)
# Nếu màn hình lớn hơn,đi đến draw_skip thông qua hàm goto_draw_skip
# Nếu màn hình bé hơn,đi đến check_error
goto_draw_skip:
	goto draw_skip
check_error:
	er2 = 0xd374
	setlr
	er0=[er2],r2 = 9,rt
	r1 = 0,rt
	er2 = 0x0061
	call 0c790
	er2 = adr_arith draw - adr_arith draw_skip,0x00
	er4 = adr_of [-2] draw_skip
	er0*=r2,er2 = er0,er0+=er4,rt
	er14 = er0,pop xr0
	0x30303030
	sp = er14,pop er14
# Trong trường hợp nhập lỗi ở D180 và EEA0, biến y sẽ quay về F3 và D3A0 sẽ quay về 00.Do đó cần CMP để tránh trường hợp hai vị trí cập nhật khác nhau trong trường hợp này
# Nếu đúng là có ERROR, đi đến draw_skip
# Nếu không,đi đến phần vẽ (Draw)
draw_skip:
	setlr
	xr0 = adr_of [+4788] update_screen_status,adr_of [+4784] pos
	[er0]=er2,rt
# Giúp vị trí cũ và vị trí mới cập nhất cùng lúc,từ đó line_draw khi chạy ở lúc đầu hay lúc cập nhật vị trí khác nhau sẽ không bị lỗi
# Ví dụ:Vị trí cũ = 00 00, vị trí mới = 20 00 thì line_draw sẽ bị nối lệch
	er14 = adr_of [-2] check_pos_x
	sp = er14,pop er14
# Đi đến check_pos_x và không vẽ bất kỳ cái gì trong trường hợp này
draw:
	er0 = 0xd3a0
	er12 = 0xd3a0
	call 16082
	call 160f8
# Đưa tổng về hex,từ đó ta có vị trí pixel x;y trên màn hình.Lúc này đây là vị trí mới
	er4 = 0x2060
	setlr
	er0+=er4,rt
# Căn chỉnh để điểm 0 nằm chính giữa màn hình
	er8 = er0
update_screen_status:
	er2 = adr_of [+4784] pos
	[er2]=er0,r2 = 0,pop er4,rt
# Nơi cập nhật 2 vị trí cùng lúc trong trường hợp có ERROR hoặc chương trình mới bắt đầu
	0x3030
	er2 = adr_of [+4784] pos
	er0=[er2],r2 = 9,rt
	er2 = er0,er0+=er4,rt
	er0 = er8
	line_draw
# Đưa vị trí cũ vào er2,vị trí mới vào er0 và line_draw
	er0 = er8
	setlr
	call 091ea
	render.ddd4
# Vẽ pixel theo vị trí mới
	xr0 = adr_of [+4788] update_screen_status,0x0000
	setlr
	[er0]=er2,rt
# Sau khi đi qua trường hợp ERROR hoặc mới khởi tạo chương trình,ta cần cái này đưa thứ tự cập nhật của 2 vị trí cũ và mới trở lại khác nhau giúp pixel không bị thiếu nét
	er0 = er8
	er2 = adr_of [+4784] pos
	[er2]=er0,r2 = 0,pop er4,rt
	0x3030
# Cập nhật vị trí cũ
check_pos_x:
	er0 = 0xd338
	num_to_byte
# Đưa giá trị của x về hex và lưu ở r0
	setlr
	r1 = 0,rt
	er2 = 0x0061
	call 0c790
	er4 = adr_of [-2] fx_to_gx
	er2 = adr_arith loop - adr_arith fx_to_gx, 0x00
	er0*=r2,er2 = er0,er0+=er4,rt
	er14 = er0,pop xr0
	0x30303030
	sp = er14,pop er14
# Kiểm tra x đã đi qua 9,6 chưa (tương đương với màn hình đã vẽ hết chưa)
# Nếu đã vẽ hết: Đi đến fx_to_gx (Tức đổi hàm từ f(x) sang g(x) nếu f(x) đã vẽ xong)
# Nếu chưa:chạy về loop
fx_to_gx:
	xr0 = adr_of [+4784] addr_input, 0xd180
	[er0]=er2,rt
# Đổi sang hàm g(x) thông qua đổi vị trí hàm tại addr_input
	xr0 = adr_of addr_set_x_2, 0xd36a
	call 17922
# Đưa lại giá trị x về -9,6 để vẽ lại từ đầu
	setlr
	xr0 = adr_of [+4788] update_screen_status,adr_of [+4784] pos
	[er0]=er2,rt
# Do đây cũng là mới khởi tạo vẽ hàm mới (g(x)) nên ta cần cái này
# Giúp vị trí cũ và vị trí mới cập nhất cùng lúc,từ đó line_draw khi chạy ở lúc đầu hay lúc cập nhật vị trí khác nhau sẽ không bị lỗi
# Ví dụ:Vị trí cũ = 00 00, vị trí mới = 20 00 thì line_draw sẽ bị nối lệch
sp:
	er14 = adr_of [-2] jump
	sp = er14,pop er14
# nhảy đến jump
enter_formula:
	xr0 = 0x0001d0f5
	[er0]=r2
# Đưa giá trị ở địa chỉ D0F5 thành 01,lúc này máy sẽ không bị tắt để trước khi bấm [Shift] máy vẫn luôn mở màn hình dù qua 10 phút.Chi tiết hãy đọc disas phần shutdown_func
	waitshift
	xr0 = 0x0000d0f5
	[er0]=r2
# Đưa lại D0F5 về 00 để màn hình nhập giá trị f(x),g(x) xuất hiện lại trỏ
	call 2e236
# Gọi hàm calc_mode để lưu hàm số từ D180 (input area)
	xr0 = 0xee80, 0xd180
	BL strcpy
# Đưa D180 lên EE80 (Vì có 2 hàm f(x),g(x) nên mỗi hàm một vùng địa chỉ
	call 2e236
# Gọi hàm calc_mode để lưu hàm số từ D180 (input area)
	setlr
	setsfr
	buffer_clear
	xr0 = adr_of addr_set_x, 0xd36a
	call 17922
# Đưa x về giá trị ban đầu (-9,6)
	xr0 = 0x0008d137
	[er0]=r2
	xr0 = adr_of [+4788] update_screen_status,adr_of [+4784] pos
	setlr
	[er0]=er2,rt
# Giúp vị trí cũ và vị trí mới cập nhất cùng lúc,từ đó line_draw khi chạy ở lúc đầu hay lúc cập nhật vị trí khác nhau sẽ không bị lỗi
# Ví dụ:Vị trí cũ = 00 00, vị trí mới = 20 00 thì line_draw sẽ bị nối lệch
	xr0 = adr_of [+4784] addr_input, 0xee80
	[er0]=er2,rt
# Đưa lại nơi input đầu tiên là EE80 như lúc mới khởi tạo program
	xr0 = adr_of [+4788] sp, adr_of [-2] jump
	[er0]=er2,rt
# Đưa lại sp về jump để cập nhật khi f(x) vẽ xong thì chuyển qua g(x) thông qua jump
	goto setup_screen
# Do nếu để setup_screen ở đây sẽ khiến r2 không còn đúng do khoảng cách từ loop đến fx_to_gx quá dài nên sẽ đưa setup_screen ra chỗ khác để r2 có thể tính đúng
jump:
	setlr
	xr0 = adr_of [+4788] sp, adr_of [-2] enter_formula
	[er0]=er2,rt
# Nếu mới vẽ xong hàm f(x),sẽ nhảy đến đây mà sp không bị đổi.Đồng thời tại đây setup lại sp thay đổi để nhảy về enter_formula (Tức là nhập lại hàm số) khi đã vẽ hết g(x)
	loop:
	setlr
	di,rt
	xr0 = adr_of segment, 0x0001
	[er0]=er2,rt
	qr0 = pr_length, adr_of [+4784] home, adr_of home, adr_of [-2] home
	hex 32 89
segment:
	adr_arith end - adr_arith segment
	hex 00 30 30
	sp = er6,pop er8
# Khôi phục lại program bị phá hủy bới stack và chạy lại từ đầu
addr_set_x:
	adr_of set_x
addr_set_x_2:
	adr_of set_x_2
addr_input:
	0xee80
addr_add_x:
	adr_of add_x
addr_int_y:
	adr_of int_y
addr_int_x:
	adr_of int_x
addr_total:
	adr_of total
# Các địa chỉ để hàm calc_mode hoạt động
set_x:
	hex c0 39 2e 36 00
# -9,6.Đưa x về giá trị này
set_x_2:
	hex c0 39 2e 36 00
# -9,6.Đưa x về giá trị này
add_x:
	hex 48 a6 30 2e 31 00
# x+0,1=x.Từ đó cập nhật được vị trí x;y mới và vị trí pixel mới
int_y:
	hex c0 83 49 a8 44 d0 00
# -Int(y×C).Lấy giá trị đã làm tròn của y nhân cho C để zoom.Lý do có dấu âm đằng trước là để khi giá trị dương thì pixel đi lên trên (Tức là y càng lớn thì pixel càng lên cao).Nếu theo logic của Casio thì vị trí y của pixel càng lớn thì y càng đi xuống nên mới có trường hợp này.
int_x:
	hex 83 48 a8 31 30 d0 00
# Int(x×10).Làm tròn x rồi nhân cho giá trị cố định là 10
total:
	hex 32 35 36 a8 42 a6 43 00
# Tính tổng theo công thức 256×y+x để có vị trí x;y ở dạng pixel thông qua hai function 1:6082 và 1:60f8 (Đọc kỹ ở trên)
pos:
	0x0000
# Địa chỉ chứa vị trí pixel cũ
setup_screen:
	xr0 = hex 61 01 11 00
	char_print
	xr0 = hex b8 18 10 00
	char_print
	xr0 = hex 58 21 30 00
	char_print
	xr0 = hex 60 40 60 00
	line_draw
	xr0 = hex 00 20 c0 20
	line_draw
	render.ddd4
# Đưa màn hình về màn hình đồ thị (Bao gồm trục,chữ x,y ...)
	goto loop
# Quay lại loop
end:
	#Launcher:
	# fd 24 30 30 da 7b 31 30 fe 02 e0 e9 30 d7 2e d7 32 89 31 30 30 30 74 1f 32 30
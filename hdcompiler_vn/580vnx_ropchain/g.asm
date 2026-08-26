org 0xd730
enter:
	call 2e236
	xr0 = 0xee80, 0xd180
	BL strcpy
	call 2e236
	xr0 = 0x0001d0f5
	[er0]=r2
	setlr
	setsfr
	buffer_clear
	xr0 = adr_of addr_set_x, 0xd36a
	call 17922
	xr0 = 0x0008d137
	[er0]=r2
	xr0 = adr_of [+4788] update_screen_status,adr_of [+4784] pos
	[er0]=er2,rt
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
home:
	setlr
	xr0 = adr_of addr_input, 0xd374
	call 17922
	xr0 = adr_of addr_add_x, 0xd36a
	call 17922
	xr0 = adr_of addr_int_y, 0xd32e
	call 17922
	xr0 = adr_of addr_int_x, 0xd338
	call 17922
	xr0 = adr_of addr_total, 0xd3a0
	call 17922
	xr0 = 0x0018ddd4
	memzero
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
draw_skip:
	setlr
	xr0 = adr_of [+4788] update_screen_status,adr_of [+4784] pos
	[er0]=er2,rt
	er14 = adr_of [-2] check_pos_x
	sp = er14,pop er14
draw:
	er0 = 0xd3a0
	er12 = 0xd3a0
	call 16082
	call 160f8
	er4 = 0x2060
	setlr
	er0+=er4,rt
	er8 = er0
update_screen_status:
	er2 = adr_of [+4784] pos
	[er2]=er0,r2 = 0,pop er4,rt
	0x3030
	er2 = adr_of [+4784] pos
	er0=[er2],r2 = 9,rt
	er2 = er0,er0+=er4,rt
	er0 = er8
	line_draw
	er0 = er8
	setlr
	call 091ea
	render.ddd4
	xr0 = adr_of [+4788] update_screen_status,0x0000
	setlr
	[er0]=er2,rt
	er0 = er8
	er2 = adr_of [+4784] pos
	[er2]=er0,r2 = 0,pop er4,rt
	0x3030
check_pos_x:
	er0 = 0xd338
	num_to_byte
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
fx_to_gx:
	xr0 = adr_of [+4784] addr_input, 0xd180
	[er0]=er2,rt
	xr0 = adr_of addr_set_x_2, 0xd36a
	call 17922
	setlr
	xr0 = adr_of [+4788] update_screen_status,adr_of [+4784] pos
	[er0]=er2,rt
	sp:
	er14 = adr_of [-2] jump
	sp = er14,pop er14
enter_formula:
	xr0 = 0x0001d0f5
	[er0]=r2
	waitshift
	xr0 = 0x0000d0f5
	[er0]=r2
	call 2e236
	xr0 = 0xee80, 0xd180
	BL strcpy
	call 2e236
	setlr
	setsfr
	buffer_clear
	xr0 = adr_of addr_set_x, 0xd36a
	call 17922
	xr0 = 0x0008d137
	[er0]=r2
	xr0 = adr_of [+4788] update_screen_status,adr_of [+4784] pos
	setlr
	[er0]=er2,rt
	xr0 = adr_of [+4784] addr_input, 0xee80
	[er0]=er2,rt
	xr0 = adr_of [+4788] sp, adr_of [-2] jump
	[er0]=er2,rt
	goto setup_screen
jump:
	setlr
	xr0 = adr_of [+4788] sp, adr_of [-2] enter_formula
	[er0]=er2,rt
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
set_x:
	hex c0 39 2e 36 00
set_x_2:
	hex c0 39 2e 36 00
add_x:
	hex 48 a6 30 2e 31 00
int_y:
	hex c0 83 49 a8 44 d0 00
int_x:
	hex 83 48 a8 31 30 d0 00
total:
	hex 32 35 36 a8 42 a6 43 00
pos:
	0x0000
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
	goto loop
end:
	#Launcher:
	# fd 24 30 30 da 7b 31 30 fe 02 e0 e9 30 d7 2e d7 32 89 31 30 30 30 74 1f 32 30
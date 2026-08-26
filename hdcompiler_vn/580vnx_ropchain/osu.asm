org 0xd730
home:
    setlr
    setsfr
    buffer_clear
print_cursor:
    xr0 = hex 60 20 08 08
    render_bitmap
    er0 = adr_of cursor
    render.ddd4
print_object:
    xr0 = hex 60 20 08 08
    render_bitmap
    er0 = adr_of object
    render.ddd4
for_check_object:
    er2 = adr_of [+4788] print_object
    setlr
    er0=[er2],r2=9,rt
    er2 = adr_of locate_table
    [er2]=er0,r2 = 0,pop er4,rt
    0x3030
check_key:
    er0 = adr_of key
    setlr
    getkey
    ea = adr_of key_table
    pop er0
key:
    hex 00 00
    call 09c20
    call 1c64a
    sp = er6,pop er8
key_up:
    er2 = 0xff00
    er8 = adr_of [+4788] print_cursor
    [er8]+=er2,pop xr8
    0x30303030
    goto check_locate
key_down:
    er2 = 0x0100
    er8 = adr_of [+4788] print_cursor
    [er8]+=er2,pop xr8
    0x30303030
    goto check_locate
key_left:
    er2 = 0xffff
    er8 = adr_of [+4788] print_cursor
    [er8]+=er2,pop xr8
    0x30303030
    goto check_locate
key_right:
    er2 = 0x0001
    er8 = adr_of [+4788] print_cursor
    [er8]+=er2,pop xr8
    0x30303030
check_locate:
    er2 = adr_of [+4788] print_cursor
    er0 = [er2],r2=9,rt
    ea = adr_of locate_table
    call 09c20
    call 1c64a
    sp = er6,pop er8
if_cursor_equal_to_object:
    xr0 = adr_of addr_random_x, 0xd32e
    call 17922
    xr0 = adr_of addr_random_y, 0xd338
    call 17922
    xr0 = adr_of addr_total, 0xd3a0
    call 17922
    er0 = 0xd3a0
    er12 = 0xd3a0
    call 16082
    call 160f8
    er2 = adr_of [+4788] print_object
    setlr
    [er2]=er0,r2=0,pop er4,rt
    0x3030
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
key_table:
    hex 40 04
    adr_of [-2] key_left
    hex 80 08
    adr_of [-2] key_right
    hex 80 04
    adr_of [-2] key_up
    hex 40 08
    adr_of [-2] key_down
    hex 00 00
    adr_of [-2] check_locate
locate_table:
    hex 30 30
    adr_of [-2] if_cursor_equal_to_object
    hex 00 00
    adr_of [-2] loop
addr_random_x:
    adr_of random_x
addr_random_y:
    adr_of random_y
addr_total:
    adr_of total
random_x:
    hex 87 30 2c 31 38 33 d0 00
random_y:
    hex 87 31 2c 35 35 d0 00
total:
    hex 32 35 36 a8 43 a6 42 00
cursor:
    hex ff ff ff ff ff ff ff ff
object:
    hex ff ff 80 01 80 01 ff ff
end:
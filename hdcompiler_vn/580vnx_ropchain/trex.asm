org 0xd730
	setlr
	setsfr
	buffer_clear
point_calc:
	xr0 = adr_of addr_add, 0xd32e
	call 17922
	xr0 = adr_of addr_int, 0xd3b0
	call 17922
	xr0 = 0xd3b0, adr_of [+4790] point_text
	setlr
	num_to_str
	xr0 = hex 00 3f c0 3f
	line_draw
	xr0 = 0x010a, adr_of [+4784] point_text
	smallprint
print_player:
	xr0 = hex 20 2e 10 10
	render_bitmap
	er0 = adr_of [+4784] player
object_value:
	er2 = 0xfffc
	er8 = adr_of [+4788] print_object
	[er8]+=er2,pop xr8
	0x30303030
	xr0 = adr_of [+4789] print_object, 0x002e
	[er0] = r2
print_object:
	xr0 = hex 00 2e 10 10
	render_bitmap
	er0 = adr_of [+4784] object
	render.ddd4
	er0 = adr_of [+4788] print_object
	setlr
	er0 = [er0],pop xr8,rt
	0x30303030
	er2 = adr_of [+4784] distance_table
	setlr
	[er2]=er0,r2 = 0,pop er4,rt
	0x3030
jump:
	er2 = 0x0000
	er8 = adr_of [+4788] print_player
	[er8]+=er2,pop xr8
	0x30303030
check_key:
	er0 = adr_of key
	getkey
	ea = adr_of key_table
	pop er0
key:
	hex 00 00
	call 09c20
	call 1c64a
	sp = er6,pop er8
key_up:
	xr0 = adr_of [+4789] print_player, 0x002c
	[er0]=r2
	xr0 = adr_of [+4788] jump, 0xfe00
	setlr
	[er0]=er2,rt
check_jump:
	ea = adr_of jump_table
	er2 = adr_of [+4788] print_player
	setlr
	er0 = [er2],r2=9,rt
	call 09c20
	call 1c64a
	sp = er6,pop er8
if_reach_max:
	xr0 = adr_of [+4788] jump, 0x0100
	setlr
	[er0]=er2,rt
	er0 = adr_of [+4790] if_flying
	[er0]=er2,rt
	xr0 = adr_of [+4790] if_reach_med,0x0200
	[er0]=er2,rt
	xr0 = adr_of [+4790] med_jump,0x0200
	[er0]=er2,rt
	goto check_distance
if_reach_min:
	xr0 = adr_of [+4788] jump, 0x0000
	setlr
	[er0]=er2,rt
	xr0 = adr_of [+4790] if_flying, 0xfe00
	[er0]=er2,rt
	xr0 = adr_of [+4790] if_reach_med,0xff00
	[er0]=er2,rt
	xr0 = adr_of [+4790] med_jump,0xff00
	[er0]=er2,rt
	xr0 = adr_of [+4788] key_up, adr_of [+4789] print_player
	[er0]=er2,rt
	goto check_distance
if_reach_med:
    xr0 = adr_of [+4790] if_flying, 0xff00
    setlr
    [er0]=er2,rt
med_jump:
    xr0 = adr_of [+4788] jump,0xff00
	[er0]=er2,rt
    goto check_distance
if_flying:
	xr0 = adr_of [+4788] jump, 0xfe00
	setlr
	[er0]=er2,rt
	xr0 = adr_of [+4788] key_up, 0x0000
	[er0]=er2,rt
check_distance:
	ea = adr_of distance_table
	er2 = adr_of [+4788] print_player
	setlr
	er0 = [er2],r2=9,rt
	call 09c20
	call 1c64a
	sp = er6,pop er8
if_touched:
	setlr
	buffer_clear
	xr0 = ,0x100e, adr_of [+4784] text_lose
	smallprint
	xr0 = 0x200a, adr_of [+4784] text
	smallprint
	xr0 = 0x2c0a,adr_of [+4784] point_text
	smallprint
	render.ddd4
	xr0 = 0xd0f5, 0x0101
	[er0]=r2
	waitshift
	xr0 = adr_of addr_set_0, 0xd32e
	call 17922
	goto loop
loop:
	setlr
	di,rt
	xr0 = adr_of segment, 0x0001
	[er0]=er2,rt
	qr0 = pr_length, 0xE9E0, 0xd730, 0xd72e
	hex 32 89
segment:
	adr_arith end - adr_arith segment
	0x000000
	sp = er6,pop er8
key_table:
	hex 80 04
	adr_of [-2] key_up
	hex 00 00
	adr_of [-2] check_jump
jump_table:
	hex 20 10
	adr_of [-2] if_reach_max
	hex 20 16
	adr_of [-2] if_reach_med
	hex 20 2e
	adr_of [-2] if_reach_min
	hex 00 00
	adr_of [-2] if_flying
distance_table:
	hex 30 30
	adr_of [-2] if_touched
	hex 00 00
	adr_of [-2] loop
addr_add:
	adr_of add
addr_int:
	adr_of int
addr_set_0:
	adr_of set_0
set_0:
	hex 30 00
add:
	hex 42 a6 30 2e 32 35 00
int:
	hex 83 42 d0 00
end:
	0x00
point_text:
	str "Score:"
	0x00
hex 00 00 00 00 00 00 00 00 00 00
player:
	hex 00 00 00 78 00 fc 00 fc 00 fc 00 f0 01 c0 27 e0 3f e0 3f c0 1f c0 0f 80 07 80 04 80 04 80 00 00
object:
	hex 03 80 07 c0 07 cf e7 cf e7 cf e7 cf e7 cf ff cf 3f cf 07 ff 07 fe 07 f8 07 c0 07 c0 07 c0 07 c0
text:
	str "Press~[Shift]~to~play~again
	0x00
text_lose:
    str "You~lose"
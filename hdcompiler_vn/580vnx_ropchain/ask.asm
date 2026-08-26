org 0xd730
    setlr
    buffer_clear
point:
    xr0 = adr_of addr_add, 0xd31a
    call 17922
    xr0 = 0xd31a, adr_of [+4790] score
    num_to_str
print_score:
    xr0 = 0x2e0a, adr_of [+4784] score
    smallprint
print_spike_1:
    xr0 = 0x3908, adr_of spike_1
    smallprint
print_spike_2:
    xr0 = 0x0108, adr_of spike_2
    smallprint
line_draw:
    xr0 = hex 00 01 c0 01
    line_draw
    xr0 = hex 00 3f c0 3f
    line_draw
    xr0 = hex 00 01 00 3f
    line_draw
    xr0 = hex bf 01 bf 3f
    line_draw
    render.ddd4
print_player:
    xr0 = hex 20 20 10 08
    render_bitmap
    er0 = adr_of [+4784] player
    render.ddd4
player_move:
    er2 = 0x0002
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
    setlr
    r0 = [ea], rt
    er2 = adr_of [+4789] player_move
    [er2]=r0,r2=0
check_pos:
    er2 = adr_of [+4788] print_player
    setlr
    er0=[er2],r2=9,rt
    r0 = 0
    ea = adr_of pos_table
    call 09c20
    call 1c64a
    sp = er6,pop er8
lose:   
    xr0 = 0x0001d0f5
    [er0]=r2
    setlr
    buffer_clear
    setsfr
    xr0 = 0x100e, adr_of text
    smallprint
    xr0 = 0x200a, adr_of text_2
    smallprint
    xr0 = 0x2c0a, adr_of [+4784] score
    smallprint
    waitshift
    xr0 = adr_of [+4788] print_player,0x2000
    setlr
    [er0]=er2,rt
    xr0 = hex 1a d3 00 00
    num_fromdigit
    goto loop
check_x:
    er2 = adr_of [+4788] print_player
    setlr
    er0=[er2],r2=9,rt
    r1=0,rt
    ea = adr_of x_table
    call 09c20
    call 1c64a
    sp = er6,pop er8
turn_x:
    xr0 = adr_of [+4788] print_player, 0x0000
    [er0]=r2
    er2 = 0x0010
    er8 = 0xf034
    [er8]+=er2,pop xr8
    0x30303030
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
addr_add:
    adr_of add
add:
    hex 40 a6 31 00
end:
key_table:
    hex 80 04
    0x00fe
    hex 00 00
    0x0002
pos_table:
    hex 00 32
    adr_of [-2] lose
    hex 00 06
    adr_of [-2] lose
    hex 00 00
    adr_of [-2] check_x
x_table:
    hex b0 00
    adr_of [-2] turn_x
    hex 00 00
    adr_of [-2] loop
player:
    hex 00 00 0E 00 0F F0 1F F8 1A 48 1F F8 0C 00 00 00
spike_1:
    hex 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14
spike_2:
    hex 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15 15
text:
    str "You~lose"
    0x00
text_2:
    str "Press~[Shift]~to~play~again"
    0x00
score:
    str "Score:"
    0x00
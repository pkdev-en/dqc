org 0xd730
    setlr
    setsfr
home:
    setlr
    buffer_clear
mov_pos_to_table:
    er2 = adr_of [+4788] print_object
    er0 = [er2],r2 =9,rt
    er2 = adr_of [+4784] touch_table
    [er2]=er0,r2 = 0,pop er4,rt
    0x3030
print_line_draw:
    xr0 = hex 3f 01 3f 40
    line_draw
    xr0 = hex 70 01 70 40
    line_draw
print_player:
    xr0 = hex 40 30 10 10
    render_bitmap
    er0 = adr_of player
print_object:
    xr0 = hex 40 00 10 10
    render_bitmap
    er0 = adr_of object
print_point:
    xr0 = 0x010a, adr_of [+4784] point_text
    smallprint
    BL render.ddd4
setup_point:
    xr0 = adr_of addr_point, 0xd32e
    call 17922
    xr0 = adr_of addr_int, 0xd3a0
    call 17922
    xr0 = 0xd3a0, adr_of [+4790] point_text
    num_to_str
    er0 = 0x0000
check_key:
    er0 = adr_of keycode
    getkey
    setlr
    ea = adr_of keytable
    pop er0
keycode:
    hex 30 30
    cmp_ea
    call 1c64a
    sp = er6,pop er8
key_left:
    xr0 = adr_of [+4788] print_player, 0x0040
    [er0]=r2
    goto check_object_pos
key_right:
    xr0 = adr_of [+4788] print_player, 0x0060
    [er0]=r2
check_object_pos:
    er2 = adr_of [+4788] print_object
    setlr
    er0 = [er2], r2 = 9,rt
    r0 = 0
    ea = adr_of object_pos_table
    cmp_ea
    call 1c64a
    sp = er6,pop er8
if_reach_max:
    setlr
    xr0 = adr_of addr_random, 0xd3b0
    call 17922
    er0 = 0xd3b0
    num_to_byte
    setlr
    er2 = adr_of [+4788] print_object
    [er2]=er0,r2 = 0,pop er4,rt
    0x3030
    xr0 = adr_of [+4789] print_object, 0x0000
    [er0]=r2
    goto check_touch
else:
    er2 = 0x0200
    er8 = adr_of [+4788] print_object
    [er8]+=er2,pop xr8
    0x30303030
check_touch:
    er2 = adr_of [+4788] print_player
    setlr
    er0 = [er2],r2 =9,rt
    er4 = 0xf400
    er0+=er4,rt
    ea = adr_of touch_table
    cmp_ea
    call 1c64a
    sp = er6,pop er8
if_touch:
    xr0 = 0x000ed0f5
    [er0]=r2
    er0 = 0xd137
    [er0]=r2
    setlr
    buffer_clear
    xr0 = 0x0c30, adr_of [+4784] text
    BL line_print
    xr0 = 0x0008d137
    [er0]=r2
    xr0 = 0x1a46, adr_of [+4784] point_text
    BL line_print
    xr0 = 0x2c30, adr_of [+4784] text_2
    BL line_print
    xr0 = 0x3430, adr_of [+4784] text_3
    BL line_print
    xr0 = hex 2e d3 0a 00
    memzero
    xr0 = adr_of [+4789] print_object,0x0000
    [er0]=r2
    waitshift
loop:
    setlr
    di,rt
    xr0 = adr_of segment, 0x0001
    [er0]=er2,rt
    qr0 = pr_length,adr_of [+4784] home, adr_of home, adr_of [-2] home
    hex 32 89
segment:
    adr_arith end - adr_arith segment
    0x000000
    sp = er6, pop er8
keytable:
    hex 40 04
    adr_of [-2] key_left
    hex 80 08
    adr_of [-2] key_right
    hex 00 00
    adr_of [-2] check_object_pos
object_pos_table:
    hex 00 36
    adr_of [-2] if_reach_max
    hex 00 00
    adr_of [-2] else
touch_table:
    0x3030
    adr_of [-2] if_touch
    0x0000
    adr_of [-2] loop
addr_random:
    adr_of random
addr_point:
    adr_of point
addr_int:
    adr_of int
int:
    hex 83 42 d0 00
random:
    hex 36 34 a6 60 33 32 a8 87 30 2c 31 d0 d0 00
point:
    hex 42 a6 30 2e 32 35 00 00
player:
    hex 00 00 00 00 00 00 03 C0 03 C0 07 E0 07 E0 03 C0 03 C0 03 C0 03 C0 07 E0 07 E0 07 E0 00 00 00 00 
object:
    hex 00 00 00 00 07 E0 07 E0 07 E0 03 C0 03 C0 03 C0 03 C0 07 E0 07 E0 03 C0 03 C0 00 00 00 00 00 00
end:
text:
    str "You~Died!"
    0x00
text_2:
    str "[Shift]:~Respawn"
    0x00
text_3:
    str "[ON]:~Exit"
    0x00
point_text:
    str "Point:"
    0x00
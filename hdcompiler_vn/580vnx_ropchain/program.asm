org 0xd730
home:
    setlr
    setsfr
    buffer_clear
print_player:
    xr0 = hex 60 20 09 09
    render_bitmap
    er0 = adr_of player_bitmap
print_object:
    xr0 = hex 60 20 09 09
    render_bitmap
    er0 = adr_of object_bitmap
print_food:
    xr0 = hex 60 20 09 09
    render_bitmap
    er0 = adr_of food_bitmap
    render.ddd4
move_position_object_to_table:
    er2 = adr_of [+4788] print_object
    setlr
    er0 = [er2],r2 = 9,rt
    er2 = adr_of [+4784] position_table
    [er2]=er0,r2 = 0,pop er4,rt
    0x3030
move_position_food_to_table:
    er2 = adr_of [+4788] print_food
    setlr
    er0 = [er2],r2 = 9,rt
    er2 = adr_of [+4784] food_table
    [er2]=er0,r2 = 0,pop er4,rt
    0x3030
check_key:
    er0 = adr_of keycode
    getkey
    pop er0
keycode:
    0x3030
    ea = adr_of keytable
    cmp_ea
    qr0=[ea],lea D002H,[ea]=qr0
    setlr
    er2 = er0,er0 = er2,pop er8,rt
    adr_of [+4788] print_player
    [er8]+=er2,pop xr8
    0x30303030
check_position:
    er2 = adr_of [+4788] print_player
    er0 = [er2],r2 = 9,rt
    ea = adr_of position_table
    cmp_ea
    er6 = [ea]
    sp = er6,pop er8
check_range_x:
    er2 = adr_of [+4788] print_player
    er0 = [er2],r2 = 9,rt
    r1 = 0,rt
    ea = adr_of range_table_x
    cmp_ea
    er6 = [ea]
    sp = er6,pop er8
min_x:
    xr0 = adr_of [+4788] print_player, 0x0004
    [er0]=r2
    goto check_range_y
max_x:
    xr0 = adr_of [+4788] print_player, 0x00b4
    [er0]=r2
check_range_y:
    er2 = adr_of [+4788] print_player
    er0 = [er2],r2 = 9,rt
    r0 = 0
    ea = adr_of range_table_y
    cmp_ea
    er6 = [ea]
    sp = er6,pop er8
min_y:
    xr0 = adr_of [+4789] print_player, 0x0004
    [er0]=r2
    goto check_object_player_x
max_y:
    xr0 = adr_of [+4789] print_player, 0x0034
    [er0]=r2
check_object_player_x:
    er2 = adr_of [+4788] print_player
    er0 = [er2],r2 = 9,rt
    r1 = 0,rt
    er2 = er0,er0+=er4,rt
    er0 = adr_of [+4788] print_object
    er0 = [er0],pop xr8,rt
    adr_of [+4788] print_object
    0x3030
    r1 = 0,rt
    er0 - er2_gt,r0 = 0 |r0 = 1,rt
    er2 = adr_arith if_object_<_player_x - adr_arith if_object_>_player_x, 0x00
    er4 = adr_of [-2] if_object_>_player_x
    er0*=r2,er2 = er0,er0+=er4,rt
    er14 = er0,pop xr0
    0x30303030
    sp = er14,pop er14
if_object_>_player_x:
    er2 = 0xffff
    [er8]+=er2,pop xr8
    0x30303030
    goto check_object_player_y
if_object_<_player_x:
    er2 = 0x0001
    [er8]+=er2,pop xr8
    0x30303030
check_object_player_y:
    er2 = adr_of [+4788] print_player
    er0 = [er2],r2 = 9,rt
    r0 = 0
    er2 = er0,er0+=er4,rt
    er0 = adr_of [+4788] print_object
    er0 = [er0],pop xr8,rt
    adr_of [+4788] print_object
    0x3030
    r0 = 0
    er0 - er2_gt,r0 = 0 |r0 = 1,rt
    er2 = adr_arith if_object_<_player_y - adr_arith if_object_>_player_y, 0x00
    er4 = adr_of [-2] if_object_>_player_y
    er0*=r2,er2 = er0,er0+=er4,rt
    er14 = er0,pop xr0
    0x30303030
    sp = er14,pop er14
if_object_>_player_y:
    er2 = 0xff00
    [er8]+=er2,pop xr8
    0x30303030
    goto loop
if_object_<_player_y:
    er2 = 0x0100
    [er8]+=er2,pop xr8
    0x30303030
    goto loop
if_eat_food:
    xr0 = adr_of addr_random_x, 0xd32e
    calc_func
    xr0 = adr_of addr_random_y, 0xd338
    calc_func
    xr0 = adr_of addr_total, 0xd3a0
    calc_func
    er12 = 0xd3a0
    cvt_hex_1
    cvt_hex_2
    er2 = adr_of [+4788] print_food
    setlr
    [er2]=er0,r2=0,pop er4,rt
    0x3030
    goto loop
if_object_touch_player:
    xr0 = 0x000ed0f5
    [er0]=r2
    er0 = 0xd137
    [er0]=r2
    setlr
    buffer_clear
    xr0 = adr_of [+4788] print_object, 0x0100
    [er0]=er2,rt
    xr0 = 0x0c30, adr_of [+4784] text_1
    BL line_print
    xr0 = 0x0008d137
    [er0]=r2
    xr0 = 0x2c30, adr_of [+4784] text_2
    BL line_print
    xr0 = 0x3430, adr_of [+4784] text_3
    BL line_print
    waitshift
loop:
    er0 = 0x0100
    delay
    xr0 = adr_of segment, 0x0001
    setlr
    [er0]=er2,rt
    qr0 = pr_length, adr_of [+4784] home, adr_of home, adr_of [-2] home
    hex 32 89
segment:
    adr_arith end - adr_arith segment
    0x000000
    sp = er6,pop er8
addr_random_x:
    adr_of random_x
addr_random_y:
    adr_of random_y
addr_total:
    adr_of total
random_x:
    hex 32 a8 87 32 2c 39 30 d0 00
random_y:
    hex 32 a8 87 32 2c 35 33 d0 00
total:
    hex 32 35 36 a8 43 a6 42 00
end:
keytable:
    hex 40 04
    0xfffe
    hex 80 08
    0x0002
    hex 80 04
    0xfe00
    hex 40 08
    0x0200
    hex 00 00
    0x0000
position_table:
    hex 30 30
    adr_of [-2] if_object_touch_player
food_table:
    hex 30 30
    adr_of [-2] if_eat_food
    hex 00 00
    adr_of [-2] check_range_x
range_table_x:
    hex b6 00
    adr_of [-2] max_x
    hex 02 00
    adr_of [-2] min_x
    hex 00 00
    adr_of [-2] check_range_y
range_table_y:
    hex 00 36
    adr_of [-2] max_y
    hex 00 02
    adr_of [-2] min_y
    hex 00 00
    adr_of [-2] check_object_player_x
player_bitmap:
    hex FF 80 80 80 80 80 80 80 80 80 80 80 80 80 80 80 FF 80
object_bitmap:
    hex 3E 00 63 00 C1 80 80 80 80 80 80 80 C1 80 63 00 3E 00
food_bitmap:
    hex FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
text_1:
    str "You~Died!"
    0x00
text_2:
    str "[Shift]:~Respawn"
    0x00
text_3:
    str "[ON]:~Exit"
    0x00
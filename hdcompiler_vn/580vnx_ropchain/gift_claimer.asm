org 0xd730
refresh_screen:
    setlr
    setsfr
    buffer_clear
print_line_draw:
    xr0 = hex 00 3f c0 3f
    line_draw
print_point:
    xr0 = 0xd32e, adr_of [+4790] score_text
    num_to_str
    er0 = 0x3030
    xr0 = 0x010a, adr_of [+4784] score_text
    smallprint
print_life:
    xr0 = 0x0c0a, adr_of [+4784] life_text
    smallprint
print_gift:
    xr0 = hex 00 00 10 10
    render_bitmap
    er0 = adr_of gift_bitmap
print_basket:
    xr0 = hex 00 2e 10 10
    render_bitmap
    er0 = adr_of basket_bitmap
    render.ddd4
gift_fall:
    er2 = 0x0200
    er8 = adr_of [+4788] print_gift
    [er8]+=er2,pop xr8
    0x30303030
move_pos_to_table_y:
    er2 = adr_of [+4788] print_basket
    setlr
    er0 = [er2],r2 = 9,rt
    r0 = 0
    er2 = adr_of [+4784] touch_table_y
    [er2]=er0,r2 = 0,pop er4,rt
    0x3030
move_pos_to_table_x:
    er2 = adr_of [+4788] print_gift
    er0 = [er2],r2 = 9,rt
    r1 = 0,rt
    er2 = adr_of [+4784] touch_table_x
    [er2]=er0,r2 = 0,pop er4,rt
    0x3030
moving_basket:
    er0 = adr_of keycode
    getkey
    pop er0
keycode:
    0x3030
    ea = adr_of move_table
    cmp_ea
    qr0=[ea],lea D002H,[ea]=qr0
    setlr
    er2 = er0, er0 = er2, pop er8,rt
    adr_of [+4788] print_basket
    [er8]+=er2,pop xr8
    0x30303030
check_range:
    er2 = adr_of [+4788] print_basket
    er0 = [er2],r2 = 9,rt
    r1 = 0,rt
    ea = adr_of range_table
    cmp_ea
    er6 = [ea]
    sp = er6,pop er8
max:
    xr0 = adr_of [+4788] print_basket, 0x00b0
    [er0]=r2
    goto check_y
min:
    xr0 = adr_of [+4788] print_basket, 0x2e00
    [er0]=er2,rt
check_y:
    er2 = adr_of [+4788] print_gift
    er0 = [er2],r2 = 9,rt
    r0 = 0
    ea = adr_of touch_table_y
    cmp_ea
    er6 = [ea]
    sp = er6,pop er8
check_x:
    er2 = adr_of [+4788] print_basket
    er0 = [er2],r2 = 9,rt
    r1 = 0,rt
    ea = adr_of touch_table_x
    cmp_ea
    er6 = [ea]
    sp = er6,pop er8
if_miss:
    er4 = adr_of [+4784] life_count
    [er4]-=1,rt
check_lose:
    er2 = adr_of [+4784] life_count
    setlr
    er0 = [er2],r2 = 9,rt
    ea = adr_of life_table
    cmp_ea
    er6 = [ea]
    sp = er6,pop er8
if_lose:
    xr0 = adr_of [+4784] life_count, 0x0033
    [er0]=r2
    xr0 = 0x000ed0f5
    [er0]=r2
    er0 = 0xd137
    [er0]=r2
    xr0 = adr_of [+4788] print_gift, 0x0060
    [er0]=er2,rt
    buffer_clear
    xr0 = 0xd32e, 0x000a
    memzero
    xr0 = 0x0c30, adr_of [+4784] text_1
    BL line_print
    xr0 = 0x0008d137
    [er0]=r2
    xr0 = 0x1a46, adr_of [+4784] score_text
    BL line_print
    xr0 = 0x2c30, adr_of [+4784] text_2
    BL line_print
    xr0 = 0x3430, adr_of [+4784] text_3
    BL line_print
    waitshift
    goto loop
if_touch:
    xr0 = adr_of addr_add_point, 0xd32e
    calc_func
setup_random:
    xr0 = adr_of addr_random, 0xd3a0
    calc_func
    er0 = 0xd3a0
    num_to_byte
    setlr
    r1 = 0,rt
    er2 = adr_of [+4788] print_gift
    [er2]=er0,r2 = 0,pop er4,rt
    0x3030
loop:
    er0 = 0x0200
    delay
    xr0 = adr_of segment, 0x0001
    [er0]=er2,rt
    qr0 = pr_length,adr_of [+4784] refresh_screen, adr_of refresh_screen, adr_of [-2] refresh_screen
    hex 32 89
segment:
    adr_arith end - adr_arith segment
    0x000000
    sp = er6, pop er8
life_text:
    str "Heart:"
life_count:
    0x0033
life_table:
    hex 30 00
    adr_of [-2] if_lose
    hex 00 00
    adr_of [-2] setup_random
move_table:
    hex 40 04
    0xfff0
    hex 80 08
    0x0010
    hex 00 00
    0x0000
touch_table_y:
    hex 00 30
    adr_of [-2] check_x
    hex 00 30
    adr_of [-2] if_miss
    hex 00 00
    adr_of [-2] loop
touch_table_x:
    hex 30 00
    adr_of [-2] if_touch
    hex 00 00
    adr_of [-2] loop
range_table:
    hex c0 00
    adr_of [-2] max
    hex f0 00
    adr_of [-2] min
    hex 00 00
    adr_of [-2] check_y
addr_random:
    adr_of random
addr_add_point:
    adr_of add_point
add_point:
    hex 42 a6 87 31 2c 33 d0 00
random:
    hex 31 36 a8 87 31 2c 31 30 d0 00
text_1:
    str "You~Lose!"
    0x00
text_2:
    str "[Shift]:~Play~:D"
    0x00
text_3:
    str "[ON]:~Exit"
    0x00
basket_bitmap:
    hex 00 00 07 E0 1F F8 38 1C 30 0C 30 0C 20 04 20 04 7F FE 7F FE 3F FC 3F FC 3F FC 3F FC 1F F8 00 00 
gift_bitmap:
    hex 1C 38 3E 7C 3F FC FF FF FF FF 82 41 FF FF 43 C2 43 C2 43 C2 43 C2 43 C2 43 C2 43 C2 43 C2 7F FE 
score_text:
    str "Score:~"
    0x00
end:
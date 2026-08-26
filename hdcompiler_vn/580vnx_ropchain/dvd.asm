org 0xd730
home:
    setlr
    setsfr
    buffer_clear
print_object:
    xr0 = hex 01 01 08 08
    render_bitmap
    er0 = adr_of [+4784] object
    render.ddd4
object_value_x:
    er2 = 0x0001
    er8 = adr_of [+4788] print_object
    [er8]+=er2,pop xr8
    adr_of [+4788] print_object
    0x3030
object_value_y:
    er2 = 0x0100
    [er8]+=er2,pop xr8
    0x30303030
check_pos_x:
    er2 = adr_of [+4788] print_object
    setlr
    er0=[er2],r2=9,rt
    r1 = 0,rt
    ea = adr_of x_table
    call 09c20
    call 1c64a
    sp = er6,pop er8
max_x:
    xr0 = adr_of [+4788] object_value_x, 0xffff
    setlr
    [er0]=er2,rt
    goto check_pos_y
min_x:
    xr0 = adr_of [+4788] object_value_x, 0x0001
    setlr
    [er0]=er2,rt
check_pos_y:
    er2 = adr_of [+4788] print_object
    setlr
    er0=[er2],r2=9,rt
    r0 = 0
    ea = adr_of y_table
    call 09c20
    call 1c64a
    sp = er6,pop er8
max_y:
    xr0 = adr_of [+4788] object_value_y, 0xff00
    setlr
    [er0]=er2,rt
    goto loop
min_y:
    xr0 = adr_of [+4788] object_value_y, 0x0100
    setlr
    [er0]=er2,rt
loop:
    di,rt
    qr8 = adr_of home, adr_of [+4784] home, 0x0060, 0x3030
    call 10F20
object:
    hex ff ff ff ff ff ff ff ff
    0x3030
    adr_of [-2] home
    sp = er6, pop er8
end:
x_table:
    hex b7 00
    adr_of [-2] max_x
    hex 01 00
    adr_of [-2] min_x
    hex 00 00
    adr_of [-2] check_pos_y
y_table:
    hex 00 37
    adr_of [-2] max_y
    hex 00 01
    adr_of [-2] min_y
    hex 00 00
    adr_of [-2] loop
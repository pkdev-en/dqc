org 0xd730
    setlr
    setsfr
setup_address:
    er12 = 0x0000
    call 134a4
add_sp:
    0x30303030303030303030
    0x30303030303030303030
    0x30303030303030303030
qr8:
    0x3030303030303030
value:
    er4 = adr_of [+4788] setup_address
    setlr
    [er4]+=1,rt
    er2 = 0xd6b2
    r0 = [er2]
print_byte:
    er2 = 0xddd4
    [er2]=r0,r2 = 0
    render.ddd4
buffer_value:
    er4 = adr_of [+4788] print_byte
    setlr
    [er4]+=1,rt
check_range:
    er2 = adr_of [+4788] print_byte
    er0 = [er2],r2 = 9,rt
    ea = adr_of table
    cmp_ea
    er6 = [ea]
    sp = er6,pop er8
if:
    xr0 = adr_of [+4788] print_byte, 0xddd4
    [er0]=er2,rt
loop:
    setlr
    di,rt
    xr0 = 0xd184d630
    BL strcpy
    er14 = 0xd62e
    sp = er14,pop er14
table:
    0xe3d4
    adr_of [-2] if
    0x0000
    adr_of [-2] loop
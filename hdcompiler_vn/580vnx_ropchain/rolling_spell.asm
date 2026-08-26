org 0xd730
home:
print_text:
    smallprint
    render.ddd4
setup_key:
    getkeycode
    ea = adr_of table
    cmp_ea
    qr0=[ea],lea D002H,[ea]=qr0
    er2 = adr_of function
    [er2]=r0,r2 = 0
    er2 = adr_of [+4786] char_table
    [er2]=r0,r2=0
    setlr_pc
    er4 = adr_of [+4784] text_address
function:
    pop pc(1:3324)
vn_char_detector_right:
    er2 = adr_of [+4784] text_address
    er0 = [er2],r2 = 9,rt
    er4 = 0xffff
    er0+=er4,rt
    r0 = [er0]
    r1 = 0,rt
    ea = adr_of char_table
    cmp_ea
    qr0=[ea],lea D002H,[ea]=qr0
    er2 = adr_of function_2
    [er2]=r0,r2 = 0
    er4 = adr_of [+4784] text_address
function_2:
    pop pc(1:3324)
vn_char_detector_left:
    er2 = adr_of [+4784] text_address
    er0 = [er2],r2 = 9,rt
    r0 = [er0]
    r1 = 0,rt
    ea = adr_of char_table
    cmp_ea
    qr0=[ea],lea D002H,[ea]=qr0
    er2 = adr_of function_3
    [er2]=r0,r2 = 0
    er4 = adr_of [+4784] text_address
function_3:
    pop pc(1:3324)
loop:
    qr0 = adr_of [+4784] home, adr_of home, 0x3030, 0x0047
    memcpy_length_rn/2, pop qr0
    0x200e
text_address:
    adr_of [+4784] text
    0x3030
    adr_of [-2] home
    sp = er6,pop er8
table:
    hex 1F FC
    0x0036
    hex 1E FC
    0x002a
char_table:
    hex F4 00
    0x002a
    hex 00 00
    0x0024
text:
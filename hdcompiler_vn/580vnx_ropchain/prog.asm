org 0xd730
home:
    setlr
    setsfr
    xr0 = 0xd0f5, 0x0002
    [er0]=r2
    er0 = 0xd111
    [er0]=r2
print_text:
    xr0 = 0x0108, 0xe3e0
    smallprint
    er0 = 0x0908
    smallprint
    er0 = 0x1108
    smallprint
    er0 = 0x1908
    smallprint
    er0 = 0x2108
    smallprint
    er0 = 0x2908
    smallprint
    er0 = 0x3108
    smallprint
    er0 = 0x3908
    smallprint
    render.ddd4
setup_key:
    er0 = 0xd580
    getkeycode
    er2 = adr_of cvt_keycode
    [er2]=r0,r2 =0
    setlr
    ea = adr_of table
    cmp_ea
    er6 = [ea]
    sp = er6,pop er8
press_hex:
    pop er0
cvt_keycode:
    0x0000
    and r0,0f
    er2 = 0xd580
    [er2]=r0,r2 = 0
    getkeycode
    setlr
    and r0,0f
    er2 = 0xd581
    [er2]=r0,r2 = 0
    er2 = 0xd580
    er0 = [er2],r2 = 9,rt
    r0 << 4,rt
    or r0,r1
typing_address:
    er2 = 0xe3e0
    [er2]=r0,r2 = 0
    er4 = adr_of [+4788] typing_address
    [er4]+=1,rt
    goto loop
key_left:
    er4 = adr_of [+4788] typing_address
    [er4]-=1,rt
    goto loop
key_right:
    er4 = adr_of [+4788] typing_address
    [er4]+=1,rt
    goto loop
key_ac:
    xr0 = adr_of [+4788] typing_address, 0xe3e0
    [er0]=er2,rt
    xr0 = 0xe3e0, 0x0100
    memzero
    setlr
    buffer_clear
loop:
    xr0 = adr_of segment, 0x0001
    [er0]=er2,rt
    qr0 = pr_length, adr_of [+4784] home, adr_of home, adr_of [-2] home
    hex 32 89
segment:
    adr_arith end - adr_arith segment
    0x000000
    sp = er6,pop er8
end:
table:
    hex 26 fc
    adr_of [-2] key_ac
    hex 1e fc
    adr_of [-2] key_right
    hex 1f fc
    adr_of [-2] key_left
    hex 31 00
    adr_of [-2] press_hex
    hex 32 00
    adr_of [-2] press_hex
    hex 33 00
    adr_of [-2] press_hex
    hex 34 00
    adr_of [-2] press_hex
    hex 35 00
    adr_of [-2] press_hex
    hex 36 00
    adr_of [-2] press_hex
    hex 37 00
    adr_of [-2] press_hex
    hex 38 00
    adr_of [-2] press_hex
    hex 39 00
    adr_of [-2] press_hex
    hex 3a 00
    adr_of [-2] press_hex
    hex 3b 00
    adr_of [-2] press_hex
    hex 3c 00
    adr_of [-2] press_hex
    hex 3d 00
    adr_of [-2] press_hex
    hex 3e 00
    adr_of [-2] press_hex
    hex 3f 00
    adr_of [-2] press_hex
    hex 00 00
    adr_of [-2] loop
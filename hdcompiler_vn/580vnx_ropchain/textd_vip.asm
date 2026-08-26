org 0xed60
home:
    setlr
    setsfr
    xr0 = 0x0600e3d4
    memzero
change_screen_buffer:
    xr0 = 0x0000d139
    [er0]=r2
print_text:
    pop xr0
    0x0108
text_address:
    0xd320
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
    render.e3d4
setup_key:
    getkeycode
    setlr
    er2 = adr_of cvt_keycode
    [er2]=r0,r2=0
    ea = adr_of keytable
    cmp_ea
    er6 = [ea]
    sp = er6,pop er8
enter_hex:
    pop er0
cvt_keycode:
    0x0000
    and r0, 0f
    er2 = 0xd182
    [er2]=r0,r2 = 0
    getkeycode
    setlr
    and r0, 0f
    er2 = 0xd183
    [er2]=r0,r2 = 0
    er2 = 0xd182
    er0 = [er2],r2=9,rt
    r0 << 4,rt
    or r0,r1
    pop er2
type_address:
    0xd320
    [er2]=r0,r2 = 0
key_right:
    er4 = adr_of [-896] type_address
    [er4]+=1,rt
    goto loop
key_left:
    er4 = adr_of [-896] type_address
    [er4]-=1,rt
    goto loop
key_up:
    er2 = 0xffe0
    er8 = adr_of [-896] text_address
    [er8]+=er2,pop xr8
    0x30303030
    goto loop
key_down:
    er2 = 0x0020
    er8 = adr_of [-896] text_address
    [er8]+=er2,pop xr8
    0x30303030
    goto loop
key_del:
    er4 = adr_of [-896] type_address
    [er4]-=1,rt
    er2 = adr_of [-896] type_address
    er0 = [er2],r2 = 9,rt
    er2 = 0x0020
    [er0]=r2
    goto loop
key_ac:
    xr0 = adr_of [-896] type_address, 0xd320
    [er0]=er2,rt
    er0 = adr_of [-896] text_address
    [er0]=er2,rt
    xr0 = 0x10b4d320
    memzero
loop:
    setlr
    di,rt
    xr0 = adr_of segment, 0x0001
    [er0]=er2,rt
    qr0 = pr_length,adr_of [-896] home, adr_of home, adr_of [-2] home
    hex 32 89
segment:
    adr_arith end - adr_arith segment
    0x000000
    sp = er6, pop er8
keytable:
    hex 1c fc
    adr_of [-2] key_up
    hex 1d fc
    adr_of [-2] key_down
    hex 1e fc
    adr_of [-2] key_right
    hex 1f fc
    adr_of [-2] key_left
    hex 26 fc
    adr_of [-2] key_ac
    hex 3e fc
    adr_of [-2] key_del
    hex 30 00
    adr_of [-2] enter_hex
    hex 31 00
    adr_of [-2] enter_hex
    hex 32 00
    adr_of [-2] enter_hex
    hex 33 00
    adr_of [-2] enter_hex
    hex 34 00
    adr_of [-2] enter_hex
    hex 35 00
    adr_of [-2] enter_hex
    hex 36 00
    adr_of [-2] enter_hex
    hex 37 00
    adr_of [-2] enter_hex
    hex 38 00
    adr_of [-2] enter_hex
    hex 39 00
    adr_of [-2] enter_hex
    hex 3a 00
    adr_of [-2] enter_hex
    hex 3b 00
    adr_of [-2] enter_hex
    hex 3c 00
    adr_of [-2] enter_hex
    hex 3d 00
    adr_of [-2] enter_hex
    hex 3e 00
    adr_of [-2] enter_hex
    hex 3f 00
    adr_of [-2] enter_hex
    hex 00 00
    adr_of [-2] loop
end:
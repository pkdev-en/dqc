org 0xE9E0
_$restore:
    xr0 = 0xd830, adr_of _$home
    BL memcpy,pop er0
    0x0101

_$home:
    BL zero_KO
    xr0 = adr_of [-1] _$text, adr_of _$text
    strcpy
    er2 = adr_of [-1] _$text
    r0 = [er2]
    er2 = adr_of [71] _$text
    [er2] = r0,r2 = 0
    xr0 = 0x02, 0x30, adr_of _$text
	setlr
    printline
    setlr
	render.ddd4
    er0 = 0x2001
    BL delay,pop xr0
	0x30303030

_$loop:
	setlr
	DI,RT
    xr0 = adr_of _$length, 0x0101
    [er0] = er2,rt
    xr0 = adr_of _$home, 0xd830
    BL memcpy,pop er0
    
_$length:
    0x0101
    
_$set_sp:
    er6 = adr_of [-2] _$home
    sp = er6,pop er8

_$text:
	0x20
org 0xE9E0
_$restore:
    xr0 = 0xd830, adr_of _$home
    BL memcpy,pop er0
    0x0101

_$font_setup:
    xr0 = 0xD129, 0x0A, 0x00 
    [er0] = r2
    er0 = 0xD137
    [er0] = r2


# Counting system
_$setup:
	setlr
	DI,RT
	xr0 = 0xEB40, 0x0000
	[er0] = er2,rt
	
_$home:
	er2 = 0x0001
	er8 = 0xEB40
	[er8]+=er2,pop xr8
	0x00000000
	

# Printing system
_$cvt_hex_to_string:
	setlr
	DI,RT
	er0 = 0xEB40
	r0 = [er0]
	hex_byte
	er4 = adr_of [+2] _$text
	[er4] = er0,pop er0,rt
	0x0000
	setlr
	DI,RT
	er0 = 0xEB41
	r0 = [er0]
	hex_byte
	er4 = adr_of _$text
	[er4] = er0,pop er0,rt
	0x0000
	
_$print:
    xr0 = 0x70, 0x10, adr_of _$text
	setlr
    line_print
	setlr
    render.ddd4
	
	
# Delay (for counting system)
_$delay:
    er0 = 0x0101
    BL delay,pop xr0
	0x00000000


# Loop + set SP system
_$loop:
    xr0 = adr_of _$length, 0x0101
    [er0] = er2,rt
    xr0 = adr_of _$home, 0xd830
    BL memcpy,pop er0
    
_$length:
    0x0101
    
_$set_sp:
    er6 = adr_of [-2] _$home
    sp = er6,pop er8


# Text adjustment
_$text:
    0x30303030
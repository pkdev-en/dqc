# Launcher (124an):
# <48 bytes> 34 7b 31 30 30 d6 e0 e9 50 94 30 30 01 01 78 5c 31 30 2e d6 60 0d 32 48


org 0xE9E0
_$restore:
    xr0 = 0xD830, adr_of _$home
    BL memcpy,pop er0
    0x0101


# Display logo system
_$display:
	setlr
	DI,RT
	er0 = 0x0000
	er2 = 0x0000
	BL memset,pop er2
	0x0000
	qr0 = 0x25, 0x16, 0x80, 0x16, 0x30303030
	call 0x09846
	0x646E
	call 0x0947e
	

# Set SFR screen part
_$matrix:
	xr0 = 0xF034, 0x3F, 0x30
	[er0] = r2
	
	
# Scrolling system
_$setup:
    er2 = 0x0000
    er0 = 0xF038
    [er0] = er2,rt

_$home:
    er2 = 0x0100
    er8 = 0xF038
    [er8]+=er2,pop xr8
    0x30303030

	
# Delay part
_$delay:
	er0 = 0x0101
	BL delay,pop xr0
	0x30303030
	
	
# Loop + set SP system
_$loop:
    xr0 = adr_of _$length, 0x0101
    [er0] = er2,rt
    xr0 = adr_of _$home, 0xD830
    BL memcpy,pop er0
    
_$length:
    0x0101
    
_$set_sp:
    er6 = adr_of [-2] _$home
    sp = er6,pop er8
org 0xd830
_$backup:
    xr0 = 0xDA00, adr_of _$print
    BL memcpy,pop er0
    0x0101
    
_$disable_interrupts:
    setlr
    DI,RT
    
_$font_size:
    xr0 = 0xD137, 0x0A, 0x30
    [er0] = r2
    er0 = 0xD129
    [er0] = r2
    
_$setup:
    xr0 = 0xe9e0, 0x00, 0x30
    num_fromdigit
    xr0 = 0xe9f0, 0x01, 0x30
    num_fromdigit
	xr0 = cursor_noflash, 0x01, 0x30
	[er0] = r2
	
_$print:
    xr0 = 0x08, 0x08, adr_of _$text
    call 0x08F80    # line_print
    call 0x0947E    # render.ddd4
	
_$loop:
    xr0 = 0xe9e0, 0xe9f0
    call 0x1652E    # num_add
    xr0 = 0xe9e0, adr_of _$text
    call 0x279B8    # num_to_str
	
_$delay:
    er0 = 0x0501
    call 0x09F3C    # delay

_$restore:
    setlr
    xr0 = adr_of _$length, 0x0101
    [er0] = er2,rt
    xr0 = adr_of _$print, 0xDA00
    BL memcpy,pop er0
    
_$length:
    0x0101
    
_$set_sp:
    er6 = adr_of [-2] _$print
    sp = er6,pop er8
	
_$text:
	0x0030
org 0xE5E0
_$backup:
    xr0 = 0xD830, adr_of _$counter_positive
    BL memcpy,pop er0
    0x0202
    
    
    
## Display a line first
_$display_first_line:
    setlr
    DI,RT
    xr0 = 0x00, 0x20, 0xC0, 0x20
    BL line_draw
    BL render.ddd4
    xr0 = 0xE0, 0x00, 0xE0, 0x40
    BL line_draw
    BL render.ddd4
    
    
    
## Start rotating system
# Part 1: Counting system
_$setup:
    xr0 = 0xE5D1, 0x20, 0x00
    [er0] = r2
    xr0 = 0xE5D3, 0x20, 0x00
    [er0] = r2
    xr0 = 0xE5D4, 0xE0, 0x00
    [er0] = r2
    xr0 = 0xE5D6, 0xE0, 0x00
    [er0] = r2
    
_$counter_positive:
    er2 = 0x0100
    er8 = 0xE5D1
    [er8] += er2,pop xr8
    0x00000000
    er2 = 0x0001
    er8 = 0xE5D6
    [er8] += er2,pop xr8
    0x00000000
    
_$counter_negative:
    setlr
    er0 = 0xE5D3
    er0 = [er0],pop xr8,rt
    0x00000000
    er2 = 0x0100
    er0 -= er2,rt
    er2 = 0xE5D3
    [er2] = er0,r2 = 0,pop er4,rt
    0x0000
    setlr
    er0 = 0xE5D4
    er0 = [er0],pop xr8,rt
    0x00000000
    er2 = 0x0001
    er0 -= er2,rt
    er2 = 0xE5D4
    [er2] = er0,r2 = 0,pop er4,rt
    0x0000

_$delay:
    er0 = 0x0001
    BL delay,pop xr0
    0x00000000


# Part 2: Display line and spin
_$line_setup:
    xr0 = 0xE5D0, 0x00, 0x00
    [er0] = r2
    xr0 = 0xE5D2, 0xC0, 0x00
    [er0] = r2
    xr0 = 0xE5D5, 0x00, 0x00
    [er0] = r2
    xr0 = 0xE5D7, 0x40, 0x00
    [er0] = r2
    
_$line:
    setlr
    er2 = 0xE5D2
    er0 = [er2],r2 = 9,rt
    er2 = er0,er0 = er2,pop er8,rt
    0x0000
    er0 = 0xE5D0
    er0 = [er0],pop xr8,rt
    0x00000000
    buffer_clear
    BL line_draw
    BL render.ddd4
    setlr
    er2 = 0xE5D6
    er0 = [er2],r2 = 9,rt
    er2 = er0,er0 = er2,pop er8,rt
    0x0000
    er0 = 0xE5D4
    er0 = [er0],pop xr8,rt
    0x00000000
    BL line_draw
    BL render.ddd4
	
	
	
## Restore the stack
_$restore:
    setlr
    xr0 = adr_of _$length, 0x0202
    [er0] = er2,rt
    xr0 = adr_of _$counter_positive, 0xD830
    BL memcpy,pop er0
    
_$length:
    0x0202
    
_$set_sp:
    er6 = adr_of [-2] _$counter_positive
    sp = er6,pop er8
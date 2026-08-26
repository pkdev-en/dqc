org 0xE9E0
_$backup:
    xr0 = 0xd830, adr_of _$home
	call 0x203c4
	
	
# Counting system
_$setup:
	xr0 = adr_of [+352] _$backup, 0x00, 0x30
	num_fromdigit
	xr0 = adr_of [+368] _$backup, 0x01, 0x30
	num_fromdigit
	
_$home:
	xr0 = adr_of [+352] _$backup, adr_of [+368] _$backup
	setlr
	num_add
	

# Print system
	er0 = adr_of [+352] _$backup
	setlr
	num_output_print
	setlr
	render.ddd4
	
	
# Delay part
	er0 = 0x0101
	BL delay,pop xr0
	0x30303030
	

# Looping system
_$loop:
    xr0 = adr_of _$home, 0xd830
    call 0x203c4
    goto _$home
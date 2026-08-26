# Launcher:
# FD 24 F0 EA A5 30 31 30 40 D7 E0 E9 30 30 30 30 50 94 30 FE 02 01 78 5C 31 30 3E D7 60 0D 32 48

org 0xD740
clear_screen:
	setlr
	buffer_clear
	render.ddd4
	
no_flash_cursor:
	xr0 = 0xD113, 0x01, 0x30
	[er0] = r2
	
print:
	er2 = 0xD182
	setlr
	er0 = [er2],r2 = 9,rt
	er2 = er0,er0 += er4,rt
	er0 = 0x0E, 0x11
	smallprint
	render.ddd4	# render.ddd4
	
home:
	er0 = 0xD720
	getscancode

key_left:
	setlr
	er2 = 0xD720
	er0 = [er2],r2 = 9,rt
	er2 = 0x40, 0x04	# R0 = KI = 40, R1 = KO = 04
	er0 - er2_eq,r0 = 1,rt
	r1 = 0,rt
	er4 = adr_of [-2] key_right
	er2 = 0x42, 0x30
	er0 *= r2,er2 = er0,er0 += er4,rt
	er14 = er0,pop xr0
	0x30303030
	sp = er14,pop er14
	
key_right:
	setlr
	er2 = 0xD720
	er0 = [er2],r2 = 9,rt
	er2 = 0x80, 0x08	# R0 = KI = 80, R1 = KO = 08
	er0 - er2_eq,r0 = 1,rt
	r1 = 0,rt
	er4 = adr_of [-2] other_key
	er2 = 0x28, 0x30
	er0 *= r2,er2 = er0,er0 += er4,rt
	er14 = er0,pop xr0
	0x30303030
	sp = er14,pop er14

other_key:
	er14 = adr_of [-2] restore
	sp = er14,pop er14
	
# press [<-] key
	er2 = 0xFFFF
	er8 = 0xD182
	[er8] += er2,pop xr8
	0x30303030
	er14 = adr_of [-2] restore
	sp = er14,pop er14
	
# press [->] key
	er2 = 0x0001
	er8 = 0xD182
	[er8] += er2,pop xr8
	0x30303030
	er14 = adr_of [-2] restore
	sp = er14,pop er14

restore:
	xr0 = 0xD640, 0xD184
	call 0x203C8	
	er14 = 0xD63E
	sp = er14,pop er14
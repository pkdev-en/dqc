org 0xD730
reset_position:
	setlr
	xr0 = 0xD722, 0x0000
	[er0] = er2,rt
	xr0 = 0xD724, 0x0000
	[er0] = er2,rt
	
no_cursor:
	xr0 = 0xD113, 0x01, 0x30
	[er0] = r2
	
clear_screen:
	setlr
	buffer_clear
	call 0x0947E	# render.ddd4
	
backup:
	xr0 = 0xE5E0, adr_of home
	BL memcpy,pop er0
	0x0310
	
home:
	er0 = 0xD720
	call 0x1F24E	# getscancode
	
key_up:
	setlr
	er2 = 0xD720
	er0 = [er2],r2 = 9,rt
	er2 = 0x80, 0x04	# R2 = KI = 80, R3 = KO = 04
	er0 - er2_eq,r0 = 1,rt
	r1 = 0,rt
	er4 = adr_of [-2] key_down
	er2 = 0x38, 0x30
	er0 *= r2,er2 = er0,er0 += er4,rt
	er14 = er0,pop xr0
	0x30303030
	sp = er14,pop er14
key_down:
	setlr
	er2 = 0xD720
	er0 = [er2],r2 = 9,rt
	er2 = 0x40, 0x08	# R2 = KI = 40, R3 = KO = 08
	er0 - er2_eq,r0 = 1,rt
	r1 = 0,rt
	er4 = adr_of [-2] key_left
	er2 = 0x38, 0x30
	er0 *= r2,er2 = er0,er0 += er4,rt
	er14 = er0,pop xr0
	0x30303030
	sp = er14,pop er14
	
# press key [up]
	er8 = 0xD722
	er2 = 0xFF00
	[er8] += er2,pop xr8
	0x30303030
	er14 = adr_of [-2] restore
	sp = er14,pop er14

	
key_left:
	setlr
	er2 = 0xD720
	er0 = [er2],r2 = 9,rt
	er2 = 0x40, 0x04	# R2 = KI = 40, R3 = KO = 04
	er0 - er2_eq,r0 = 1,rt
	r1 = 0,rt
	er4 = adr_of [-2] key_right
	er2 = 0x38, 0x30
	er0 *= r2,er2 = er0,er0 += er4,rt
	er14 = er0,pop xr0
	0x30303030
	sp = er14,pop er14

# press key [down]
	er8 = 0xD722
	er2 = 0x0100
	[er8] += er2,pop xr8
	0x30303030
	er14 = adr_of [-2] restore
	sp = er14,pop er14
	
key_right:
	setlr
	er2 = 0xD720
	er0 = [er2],r2 = 9,rt
	er2 = 0x80, 0x08	# R2 = KI = 80, R3 = KO = 08
	er0 - er2_eq,r0 = 1,rt
	r1 = 0,rt
	er4 = adr_of [-2] key_equal
	er2 = 0x38, 0x30
	er0 *= r2,er2 = er0,er0 += er4,rt
	er14 = er0,pop xr0
	0x30303030
	sp = er14,pop er14

# press key [left]
	er8 = 0xD724
	er2 = 0x00FF
	[er8] += er2,pop xr8
	0x30303030
	er14 = adr_of [-2] restore
	sp = er14,pop er14
	
key_equal:
	setlr
	er2 = 0xD720
	er0 = [er2],r2 = 9,rt
	er2 = 0x01, 0x40	# R2 = KI = 01, R3 = KO = 40
	er0 - er2_eq,r0 = 1,rt
	r1 = 0,rt
	er4 = adr_of [-2] key_del
	er2 = 0x38, 0x30
	er0 *= r2,er2 = er0,er0 += er4,rt
	er14 = er0,pop xr0
	0x30303030
	sp = er14,pop er14

# press key [right]
	er8 = 0xD724
	er2 = 0x0001
	[er8] += er2,pop xr8
	0x30303030
	er14 = adr_of [-2] restore
	sp = er14,pop er14

key_del:
	setlr
	er2 = 0xD720
	er0 = [er2],r2 = 9,rt
	er2 = 0x04, 0x08	# R2 = KI = 04, R3 = KO = 08
	er0 - er2_eq,r0 = 1,rt
	r1 = 0,rt
	er4 = adr_of [-2] key_ac
	er2 = 0x38, 0x30
	er0 *= r2,er2 = er0,er0 += er4,rt
	er14 = er0,pop xr0
	0x30303030
	sp = er14,pop er14

# press key [equal]
	setlr
	er2 = 0xD724
	er0 = [er2],r2 = 9,rt
	er2 = er0,er0 = er2,pop er8,rt
	0x3030
	er0 = 0xD722
	er0 = [er0],pop xr8,rt
	0x30303030
	r0 = r2
	er2 = 0x0000
	pixel_draw
	call 0x0947E
	er14 = adr_of [-2] restore
	sp = er14,pop er14
	
key_ac:
	setlr
	er2 = 0xD720
	er0 = [er2],r2 = 9,rt
	er2 = 0x04, 0x10	# R2 = KI = 04, R3 = KO = 10
	er0 - er2_eq,r0 = 1,rt
	r1 = 0,rt
	er4 = adr_of [-2] other_key
	er2 = 0x0A, 0x30
	er0 *= r2,er2 = er0,er0 += er4,rt
	er14 = er0,pop xr0
	0x30303030
	sp = er14,pop er14

# press key [del]
	setlr
	er2 = 0xD724
	er0 = [er2],r2 = 9,rt
	er2 = er0,er0 = er2,pop er8,rt
	0x3030
	er0 = 0xD722
	er0 = [er0],pop xr8,rt
	0x30303030
	r0 = r2
	er2 = 0x0101
	pixel_draw
	call 0x0947E
	er14 = adr_of [-2] restore
	sp = er14,pop er14
	
other_key:
	er14 = adr_of [-2] restore
	sp = er14,pop er14

# press key [ac]
	buffer_clear
	call 0x0947E
	er14 = adr_of [-2] restore
	sp = er14,pop er14

restore:
	setlr
	xr0 = adr_of length, 0x0310
	[er0] = er2,rt
	xr0 = adr_of home, 0xE5E0
	BL memcpy,pop er0
length:
	0x0310
set_sp:
	er14 = adr_of [-2] home
	sp = er14,pop er14
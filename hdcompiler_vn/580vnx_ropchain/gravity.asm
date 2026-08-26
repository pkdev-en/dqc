org 0xe9e0
backup is 0xD830
addrcopy is setup
backup:
	xr0 = 0xD830, adr_of setup
	BL memcpy,pop er0
	pr_length
setup:
	setlr
	di,rt
	buffer_clear
	pop xr0
x:
	0x20
y:
	0x20
sizex:
	0x08
sizey:
	0x08
	render_bitmap
	er0 = adr_of bitmap
	render.ddd4
check:
	setlr
	er0 = adr_of [-4542] y
	r0=[er0]
	er2 = hex 20 00
	r1 = 0,rt
	er8 = er0
	er0 - er2_eq,r0 = 1,rt
	er2 = adr_arith getkey - adr_arith sub, 0x00
	er4 = adr_of sub
	er0*=r2,er2 = er0,er0+=er4,rt
	er6 = er0,er0 = er8,pop qr8
	hex 00 00 00 00 00 00 00 00
	sp = er6,pop er8
sub:
	adr_of [-4542] y
	er2 = hex 00 01
	[er8]+=er2,pop xr8
	0x00000000
	goto loop
getkey:
	adr_of key
	er14 = adr_of [-12] checkkey
	getkey
	hex 00 00 00 00
key:
	hex 00 00 00 00 00 00 00 00
checkkey:
	setlr
	er0 = er8
	er2 = hex 80 04
	er0 - er2_eq,r0 = 1,rt
	r1 = 0,rt
	er2 = adr_arith jump - adr_arith [-2] checkkeymove, 0x00
	er4 = adr_of [-2] checkkeymove
	er0*=r2,er2 = er0,er0+=er4,rt
	er6 = er0,er0 = er8,pop qr8
	hex 00 00 00 00 00 00 00 00
	sp = er6,pop er8
checkkeymove:
	er8 = er0
	er2 = hex 80 08
	er0 - er2_eq,r0 = 1,rt
	r1 = 0,rt
	er2 = adr_arith right - adr_arith [-2] checkkeymove2, 0x00
	er4 = adr_of [-2] checkkeymove2
	er0*=r2,er2 = er0,er0+=er4,rt
	er6 = er0,er0 = er8,pop qr8
	hex 00 00 00 00 00 00 00 00
	sp = er6,pop er8
jump:
	adr_of [-4542] y
	er2 = hex 00 ff
	[er8]+=er2,pop xr8
	0x00000000
	setlr
	di,rt
	buffer_clear
	er2 = adr_of [-4542] y
	er0=[er2],r2 = 9,rt
	er2 = 0x0808
	render_bitmap
	er0 = adr_of bitmap
	render.ddd4
checkjump:
	setlr
	er0 = adr_of [-4542] y
	r0=[er0]
	r1=0,rt
	er2 = hex 10 00
	er0 - er2_eq,r0 = 1,rt
	er2 = adr_arith [-2] loop - adr_arith jump, 0x00
	er4 = adr_of jump
	er0*=r2,er2 = er0,er0+=er4,rt
	er6 = er0,er0 = er8,pop qr8
	hex 00 00 00 00 00 00 00 00
set_segment_up:
	setlr
	di,rt
	er0 = 0x0101
	delay
	xr0 = adr_of length_up, 0x0001
	[er0]=er2,rt
loop_up:
	xr0 = pr_length, 0xD830
	er4 = adr_of setup
	0x8932
length_up:
	adr_arith skibidi - adr_arith copy
copy:
	0x00
	0x0000
	sp=er6,pop er8
checkkeymove2:
	er2 = hex 40 04
	er0 - er2_eq,r0 = 1,rt
	r1 = 0,rt
	er2 = adr_arith left - adr_arith forgetkey, 0x00
	er4 = adr_of forgetkey
	er0*=r2,er2 = er0,er0+=er4,rt
	er6 = er0,er0 = er8,pop qr8
	hex 00 00 00 00 00 00 00 00
	sp = er6,pop er8
right:
	adr_of [-4542] x
	er2 = 0x0001
	[er8]+=er2,pop xr8
	0x00000000
	goto loop
loop:
	pop xr8
	hex 01 01
forgetkey:
	hex 00 05
	er0 = er8
	delay
	loop580
left:
	adr_of [-4542] x
	er2 = 0xFFFF
	[er8]+=er2,pop xr8
	0x00000000
	goto loop
bitmap:
hex FF FF FF FF
hex FF FF FF FF
hex FF FF FF FF
hex FF FF FF FF
hex FF FF FF FF
hex FF FF FF FF
hex FF FF FF FF
hex FF FF FF FF
hex FF FF FF FF
hex FF FF FF FF
hex FF FF FF FF
hex FF FF FF FF
hex FF FF FF FF
hex FF FF FF FF
hex FF FF FF FF
hex FF FF FF FF
skibidi:
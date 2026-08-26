org 0xE9E0
getkey:
    adr_of key
    er14 = adr_of [-12] cvtkey
    getkey
    hex 00 00 00 00
key:
    hex 00 00 00 00 00 00 00 00
cvtkey:
    xr0 = adr_of key, adrcvtkey
    setlr
    di,rt
    buffer_clear
    cvt_key
cmpkey0:
    er8 = er0
    er2 = hex 30 00
    setlr
	er0 - er2_eq,r0 = 1,rt
	r1 = 0,rt
	er2 = adr_arith key0 - adr_arith cmpkey1, 0x00
	er4 = adr_of [-2] cmpkey1
	er0*=r2,er2 = er0,er0+=er4,rt
	er6 = er0,er0 = er8,pop qr8
	hex 00 00 00 00 00 00 00 00
	sp = er6,pop er8
cmpkey1:
    er8 = er0
    er2 = hex 31 00
    setlr
	er0 - er2_eq,r0 = 1,rt
	r1 = 0,rt
	er2 = adr_arith key1 - adr_arith cmpkeyac, 0x00
	er4 = adr_of [-2] cmpkeyac
	er0*=r2,er2 = er0,er0+=er4,rt
	er6 = er0,er0 = er8,pop qr8
	hex 00 00 00 00 00 00 00 00
	sp = er6,pop er8
key0:
    er2 = adr_of x
    er0=[er2],r2 = 9,rt
    call 0x091E6
    render.ddd4
    goto set_segment
cmpkeyac:
    er8 = er0
    er2 = hex 26 FC
    setlr
	er0 - er2_eq,r0 = 1,rt
	r1 = 0,rt
	er2 = adr_arith keyac - adr_arith cmpkey, 0x00
	er4 = adr_of [-2] cmpkey
	er0*=r2,er2 = er0,er0+=er4,rt
	er6 = er0,er0 = er8,pop qr8
	hex 00 00 00 00 00 00 00 00
	sp = er6,pop er8
key1:
    er2 = adr_of x
    er0=[er2],r2 = 9,rt
    call 0x091EA
    render.ddd4
    goto set_segment
cmpkey:
    er8 = er0
    er2 = hex 1B FC
	er0 - er2_gt,r0 = 0 |r0 = 1,rt
	r1 = 0,rt
	er2 = adr_arith set_segment - adr_arith cmpkeyagain, 0x00
	er4 = adr_of [-2] cmpkeyagain
	er0*=r2,er2 = er0,er0+=er4,rt
	er6 = er0,er0 = er8,pop qr8
	hex 00 00 00 00 00 00 00 00
	sp = er6,pop er8
keyac:
    setlr
    di,rt
    buffer_clear
    render.ddd4
    goto set_segment
cmpkeyagain:
    er8 = er0
    r1 = 0,rt
    er4 = hex 20 00
    er2 = er0,r0 = r4,r1 = 0,pop xr4,rt
    adr_of [-2] jump
	er0 - er2_gt,r0 = 0 |r0 = 1,rt
	r1 = 0,rt
	er2 = adr_arith set_segment - adr_arith jump, 0x00
	er0*=r2,er2 = er0,er0+=er4,rt
	er6 = er0,er0 = er8,pop qr8
	hex 00 00 00 00 00 00 00 00
	sp = er6,pop er8
jump:
    er2 = hex 1C FC
    er0-=er2,rt
    er2 = adr_arith keydown - adr_arith keyup, 0x00
    er4 = adr_of [-2] keyup
	er0*=r2,er2 = er0,er0+=er4,rt
	er14 = er0,pop xr0
	hex 00 00 00 00
	sp = er14,pop er14
keyup:
    er8 = adr_of y
    er2 = 0x0001
    [er8]+=er2,pop xr8
    hex 00 00 00 00
    goto set_segment
keydown:
    er8 = adr_of y
    er2 = 0xFFFF
    [er8]+=er2,pop xr8
    hex 00 00 00 00
    goto set_segment
keyright:
    er8 = adr_of x
    er2 = 0x0001
    [er8]+=er2,pop xr8
    hex 00 00 00 00
    goto set_segment
keyleft:
    er8 = adr_of x
    er2 = 0xFFFF
    [er8]+=er2,pop xr8
    hex 00 00 00 00
    goto set_segment
set_segment:
	setlr
	di,rt
	er0 = adr_of length
	er2 = 0x0001
    [er0]=er2,rt
loop:
	qr0 = pr_length, 0xd830, adr_of getkey, adr_of getkey
	hex 32 89
length:
	hex 08 00 00 00
	sp = er6,pop er8
x:
    0x00
y:
    0x01
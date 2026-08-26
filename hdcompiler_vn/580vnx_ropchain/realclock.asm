# Launcher (124an)
# <48 bytes> 34 7b 31 30 30 d8 e0 e9 50 94 30 30 02 02 78 5c 31 30 2e d8 60 0d 32 48  


org 0xE9E0
setbkp:
	xr0 = 0xEB40, adr_of RTCCount
	setlr
	smart_strcpy

RTCControl:
	setlr
	DI,RT
	xr0 = 0xF0C7, 0x00, 0x00
	[er0] = r2
	xr0 = 0xF0C0, 0x00, 0x00
	[er0] = r2
	xr0 = 0xF0C1, 0x00, 0x00
	[er0] = r2
	xr0 = 0xF0C2, 0x00, 0x00
	[er0] = r2
	xr0 = 0xF0C7, 0x01, 0x00
	[er0] = r2

RTCCount:
	er0 = 0xF0C0
	r0 = [er0]
	hex_byte #convert r0 to 2-bytes 
	er4 = adr_of [+13] clock
	[er4] = er0,pop er0,rt
	0x3030
	er0 = 0xF0C1
	r0 = [er0]
	hex_byte #convert r0 to 2-bytes 
	er4 = adr_of [+9] clock
	[er4] = er0,pop er0,rt
	0x3030
	er0 = 0xF0C2
	r0 = [er0]
	hex_byte #convert r0 to 2-bytes 
	er4 = adr_of [+5] clock
	[er4] = er0,pop er0,rt
	0x3030

RTCPrint:
	xr0 = 0x21, 0x30, adr_of clock
	setlr
	printline
	setlr
	render.ddd4

custom_print:
	xr0 = 0x11, 0x30, adr_of custom_text
	setlr
	printline
	setlr
	render.ddd4

restore:
	xr0 = adr_of RTCCount, 0xEB40
	setlr
	smart_strcpy
	er14 = adr_of [-2] RTCCount
	sp = er14, pop er14

clock:
	0x202020202020013A2020013A202020202020

custom_text:
	0x216E6F676E208CF4676E2079F46220638AF46843
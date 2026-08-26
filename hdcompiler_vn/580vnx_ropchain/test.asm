backup is 0xD830
addrcopy is home
org 0xE9E0
	backup580
home:
	setlr
	di,rt
	buffer_clear
    xr0 = 0xD137, hex 0a 00
    [er0] = r2
    xr12 = adr_of font, adr_of jump
    xr4 = hex 08 00 09 09
    call 090D2
    hex 30 31           # [FP-10]   (how many bytes in font)
    hex 00 00           # [FP-8]    pad
    hex 08 00           # [FP-6]    character width and 8-character width
    hex D3 E3           # [FP-4]    end addr screen
    hex 00 18           # [FP-2]    pad and end line    
jump:
    hex 00 00 00 00 00 00 00 00        #QR8
    hex 00 00 00 00                    #XR4
    render.ddd4
	loop580
font:
    hex E0 E0
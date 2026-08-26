org 0xE9E0
home:
	setlr
	di,rt
	buffer_clear
	xr0 = 0x0100, 0x01, 0x00
	pixel_draw
	render.ddd4
	brk
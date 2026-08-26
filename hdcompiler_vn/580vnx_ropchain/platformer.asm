org 0xe9e0
setlr
setsfr
di,rt
buffer_clear
cursor_no_flash:
  xr0 = 0x0001d113
  [er0]=r2
linedraw:
  xr0=0x3800, 0x384E
  line_draw
  xr0=0x3860, 0x38C0
  line_draw
block:
  pop xr0
    posx:
    0x3001
    0x0808
  render_bitmap
  er0=adr_of bitmap
  render.ddd4
  setlr
  er0=adr_of posx
  er0=[er0],pop xr8,rt
  0x30303030
  er2=adr_of a
  [er2]=r0,r2 = 0
  er2=adr_of b
  [er2]=r0,r2 = 0
auto_down/up:
  pop er2
  c:
    0x0000
  er8=adr_of posx
  [er8]+=er2, pop xr8
  0x30303030
cmp:
  setlr
  er2=adr_of posx
  call 13b9e
  pop er2
  a:
    0x2001
  er0 - er2_eq,r0 = 1,rt
  0x3032AC30
  er4=0xD7EA
  er2=0x0038
  er0*=r2,er2 = er0,er0+=er4,rt
  er14=er0,pop xr0
  0x30303030
  sp=er14, pop er14
cmp2:
  setlr
  er2=adr_of posx
  call 13b9e
  pop er2
  b:
  0x3001
  er0 - er2_eq,r0 = 1,rt
  0x3032AC30
  er4=0xD83A
  er2=0x000A
  er0*=r2,er2 = er0,er0+=er4,rt
  er14=er0,pop xr0
  0x30303030
  sp=er14, pop er14
cmp_1_func:
  xr0=adr_of c, 0x0100
  [er0]=er2,rt
  xr0=adr_of [+4] setsp&othervalue, 0xD8DC
  [er0]=er2,rt
  setsp&othervalue:
    er14=0xD85C
    sp=er14, pop er14
cmp_2_func:
  xr0=adr_of c, 0x0000
  [er0]=er2,rt
  xr0=adr_of [+4] setsp&othervalue, 0xD85C
  [er0]=er2,rt
setupkey:
  er0 = adr_of key
  getkey
  xr12=adr_of table, adr_of table
  setlr
  call 17CA6
  pop er0
  key:
    0x0000
    call 09C20
    call 1C64A
    sp = er6, pop er8
key_right_func:
  er2=0x0001
  er8=adr_of posx
  [er8]+=er2, pop xr8
  0x30303030
  er14=0xD8D0
  sp=er14, pop er14
key_left_func:
  er2=0xFFFF
  er8=adr_of posx
  [er8]+=er2, pop xr8
  0x30303030
  er14=0xD8D0
  sp=er14, pop er14
key_up_func:
  xr0=adr_of c, 0xFF00
  [er0]=er2,rt
0:
  xr0=adr_of key, 0xFFFF
  [er0]=er2,rt
loop:
  xr0 = 0xd184d630
  BL strcpy
  er14 = 0xd62e
  sp = er14,pop er14
bitmap:
  0xFFFFFFFFFFFFFFFF
table:
  0x00000000000000000000
  0x0480
  0xD8C4
  0x0880
  0xD888
  0x0440
  0xD8A6
  0x0000
  0xD8DC
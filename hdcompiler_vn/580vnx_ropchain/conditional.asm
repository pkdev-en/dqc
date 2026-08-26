org 0xD830
home:
er0 = 0x0303
er2 = 0x0202
setlr
er0 - er2_gt,r0 = 0 |r0 = 1,rt
r1 = 0
er2 = adr_of tbl
load_table
er14 = er0, pop xr0
0x30303030
sp = er14,pop er14
0x3030

ra:
er0 = 0xF840
er2 = 0xFFFF
[er0]=er2,rt
brk

rb:
er0 = 0xF840
er2 = 0x1010
[er0]=er2,rt
brk

tbl:
adr_of [-2] ra
adr_of [-2] rb
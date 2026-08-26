org 0xd730
xr0 = 0x0015f031
[er0]=r2
xr0 = 0x010e, adr_of text
smallprint
render.ddd4
er0 = adr_of key
call 2f5ea
xr12 = adr_of [-10] table, adr_of [-10] table
setlr
call 17CA6
pop er0
key:
hex 00 00
call 09C20
call 1C64A
sp = er6, pop er8
key_1:
er2 = 0x0101
er8 = 0xf039
[er8]+=er2,pop xr8
0x30303030
loop:
xr0 = 0xd184d630
BL strcpy
er14 = 0xd62e
sp = er14,pop er14
table:
hex 01 01
adr_of [-2] key_1
hex 00 00
adr_of [-2] loop
text:
str "Hello~world"
org 0xe9e0
backup is 0xd830
addrcopy is getkey
backup:
xr0 = 0xd830, adr_of getkey
BL memcpy,pop er0
pr_length

getkey:
er0 = adr_of key
call 2F5EA
xr12 = adr_of [-10] table, adr_of [-10] table
setlr
call 17CA6
pop er0

key:
hex 00 00
call 09C20
call 1C64A
sp = er6, pop er8

key1:
xr0 = adr_of [e9ee -> d830] addrjumpkey, adr_of [-2] set_segment
setlr
[er0]=er2,rt
er4 = 0xd820
call 1332a
goto set_segment

setnormal:
xr0 = adr_of [e9ee -> d830] addrjumpkey, adr_of [-2] key1
setlr
[er0]=er2,rt

loop580

table:
0x0101
addrjumpkey:
adr_of [-2] key1
0x0000
adr_of [-2] setnormal

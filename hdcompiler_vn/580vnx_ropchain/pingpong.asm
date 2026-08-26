org 0xd830

home:
get_key:
 adr_of y
 er14 = adr_of x
 call 0x2F5F0
x:
 0x00000000
y:
 0x0000000000000000

clear:
 xr0 = 0xddd4, 0x0600
 memzero

set_paddle:
 xr0 = 0x0a, 0x18, adr_of text_paddle
 smallprint

set_ball_y:
 er0 = 0x00, 0x1f

set_ball_x:
 r0 = 0x60
 0x00
 er2 = adr_of text_ball
 line_print
 render.ddd4

key_down:
 er0 = er8
 setlr
 di, rt
 er2 = 0x40, 0x08
 er0 - er2_eq,r0 = 1,rt
 er4 = adr_of [-2] key_up
 er2 = adr_arith [-2] paddle_down - adr_arith [-2] key_up, 0x00
 er0*=r2,er2 = er0,er0+=er4,rt
 er6 = er0,er0 = er8,pop qr8
 0x3030303030303030
 sp = er6, pop er8

key_up:
 er8 = er0
 er2 = 0x80, 0x04
 er0 - er2_eq,r0 = 1,rt
 er4 = adr_of [-2] key_other
 er2 = adr_arith [-2] paddle_up - adr_arith [-2] key_other, 0x00
 er0*=r2,er2 = er0,er0+=er4,rt
 er6 = er0,er0 = er8,pop qr8
 0x3030303030303030
 sp = er6, pop er8

key_other:
 er6 = adr_of [-2] loop_ball_x
 sp = er6, pop er8
 adr_of [+4520] set_paddle

paddle_down:
 er2 = 0x0100
 [er8]+=er2,pop xr8
 0x30303030
 er6 = adr_of [-2] loop_ball_x
 sp = er6, pop er8
 adr_of [+4520] set_paddle

paddle_up:
 er2 = 0xff00
 [er8]+=er2,pop xr8
 0x00000000

loop_ball_x:
 er2 = 0x01, 0x00
 er8 = adr_of [+4520] set_ball_x
 [er8]+=er2,pop xr8
 0x00000000

loop_ball_y:
 er2 = 0x00, 0x01
 er8 = adr_of [+4520] set_ball_y
 [er8]+=er2,pop xr8
 0x00000000

delay:
 er0 = 0x0200
 delay

collide_y_01:
 setlr
 qr0 = adr_of [+4520] set_ball_y, 0x00, 0x00, 0x00, 0xfd, 0x0000
 er0=[er0],pop xr8,rt
 0x00000000
 call 27e78
 adr_of [-2] reverse_0y
 0x0000
 er2 = adr_arith [-2] collide_y_35 - adr_arith [-2] reverse_0y, 0x00
 er0*=r2,er2 = er0,er0+=er4,rt
 er6 = er0,er0 = er8,pop qr8
 0x0101010101010101
 sp = er6, pop er8

reverse_0y:
 er6 = adr_of [-2] reverse_y
 sp = er6, pop er8

collide_y_35:
 setlr
 qr0 = adr_of [+4520] set_ball_y, 0x00, 0x00, 0x00, 0x34, 0x0000
 er0=[er0],pop xr8,rt
 0x00000000
 call 27e78
 adr_of [-2] collide_paddle_1
 0x0000
 er2 = adr_arith [-2] reverse_y - adr_arith [-2] collide_paddle_1, 0x00
 er0*=r2,er2 = er0,er0+=er4,rt
 er6 = er0,er0 = er8,pop qr8
 0x0101010101010101
 sp = er6, pop er8

collide_paddle_1:
 setlr
 er8 = adr_of [+4520] set_ball_x
 er4=[er8],pop er8,rt
 0x0000
 call 0x13ad0
 er0 = adr_of [+4520] set_paddle
 er0=[er0],pop xr8,rt
 0x00000000
 r0 = 0x09
 0x00
 er0 - er2_eq,r0 = 1,rt
 er4 = adr_of [-2] collide_paddle_2
 er2 = adr_arith [-2] reverse_x - adr_arith [-2] collide_paddle_2, 0x00
 er0*=r2,er2 = er0,er0+=er4,rt
 er6 = er0,er0 = er8,pop qr8
 0x0101010101010101
 sp = er6, pop er8

reverse_y:
 er0 = adr_of [+4521] loop_ball_y
 call 0x15E38
 call 0x094f4
 0x30303030
 er2 = adr_of [+4521] loop_ball_y
 call 09b5a
 er6 = adr_of [-2] restore
 sp = er6, pop er8

collide_paddle_2:
 setlr
 er8 = adr_of [+4520] set_ball_x
 er4=[er8],pop er8,rt
 0x0000
 call 0x13ad0
 er0 = adr_of [+4520] set_paddle
 er0=[er0],pop xr8,rt
 0x00000000
 r0 = 0xb4
 0x00
 er0 - er2_eq,r0 = 1,rt
 er4 = adr_of [-2] collide_x_00
 er2 = adr_arith [-2] reverse_x - adr_arith [-2] collide_x_00, 0x00
 er0*=r2,er2 = er0,er0+=er4,rt
 er6 = er0,er0 = er8,pop qr8
 0x0101010101010101
 sp = er6, pop er8

collide_x_00:
 setlr
 er2 = adr_of [+4520] set_ball_x
 er0=[er2],r2 = 9,rt
 er2 = 0x00, 0x00
 er0 - er2_eq,r0 = 1,rt
 er4 = adr_of [-2] collide_x_c0
 er2 = adr_arith [-2] reverse_reset - adr_arith [-2] collide_x_c0, 0x00
 er0*=r2,er2 = er0,er0+=er4,rt
 er6 = er0,er0 = er8,pop qr8
 0x0101010101010101
 sp = er6, pop er8

reverse_x:
 er0 = adr_of [+4520] loop_ball_x
 call 0x15E38
 call 0x094f4
 0x30303030
 er2 = adr_of [+4520] loop_ball_x
 call 09b5a
 er6 = adr_of [-2] restore
 sp = er6, pop er8

collide_x_c0:
 er2 = adr_of [+4520] set_ball_x
 er0=[er2],r2 = 9,rt
 call 0x0AF3C
 er4 = adr_of [-2] no_collide
 er2 = adr_arith [-2] reverse_reset - adr_arith [-2] no_collide, 0x00
 er0*=r2,er2 = er0,er0+=er4,rt
 er6 = er0,er0 = er8,pop qr8
 0x0101010101010101
 sp = er6, pop er8

no_collide:
 er6 = adr_of [-2] restore
 sp = er6, pop er8

reverse_reset:
 xr0 = adr_of [+4520] set_ball_x, 0x0060
 [er0]=er2,rt
 xr0 = adr_of [+4520] set_ball_y, 0x1f00
 [er0]=er2,rt
 xr0 = adr_of [+4520] set_paddle, 0x180a
 [er0]=er2,rt

restore:
 di, rt
 er8 = adr_of length
 er2 = 0x01, 0x00
 [er8] = er2,pop xr8
 0x00000000
 qr0 = 0x0418, 0xe9d4, adr_of home, adr_of home
 0x8932

length:
 0x000e
 0x0000
 sp = er6 , pop er8

text_ball:
 0x006f

text_paddle:
 0x00007C20202020202020202020202020202020202020202020202020202020207C20
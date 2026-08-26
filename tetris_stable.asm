# Game Tetris & Arcade Engine Hoan Chinh cho Casio fx-580VN X
org 0xd730

home:
    setlr
    setsfr
    buffer_clear

    # 1. Ve tuong bao san dau (Left X=40, Right X=140, Bottom Y=56)
    xr0 = hex 28 04 28 38
    line_draw
    render.ddd4

    xr0 = hex 8c 04 8c 38
    line_draw
    render.ddd4

    xr0 = hex 28 38 8c 38
    line_draw
    render.ddd4

    # 2. In tieu de Game & Score
    xr0 = 0x3001, adr_of title_txt
    printline
    render.ddd4

    # 3. Ve khoi gach Tetromino (8x8 Sprite tai px, py)
print_block:
    xr0 = hex 58 08 08 08
    render_bitmap
    er0 = adr_of [+4784] tetromino_sprite
    render.ddd4

    # 4. Ve cac khoi gach da ha canh duoi day (Landed Pile Blocks)
    xr0 = hex 2c 30 38 30
    line_draw
    render.ddd4

    xr0 = hex 7c 30 88 30
    line_draw
    render.ddd4

    # 5. Tang toa do Y (Khoi roi xuong)
block_val_y:
    er2 = 0x0100
    er8 = adr_of [+4788] print_block
    [er8]+=er2,pop xr8
    adr_of [+4788] print_block
    0x3030

    # 6. Kiem tra va cham san (Floor Y = 46)
check_bottom:
    er2 = adr_of [+4788] print_block
    setlr
    er0=[er2],r2=9,rt
    r0 = 0
    ea = adr_of bottom_table
    call 09c20
    call 1c64a
    sp = er6,pop er8

reset_top:
    # Reset vi tri khoi len dinh
    xr0 = adr_of [+4788] block_val_y, 0x0000
    setlr
    [er0]=er2,rt
    goto loop

loop:
    # 7. Delay va Re-arm an toan (Copy dung 0x0060 bytes de KHONG de vao loop)
    er0 = 0x0050
    delay
    di,rt
    qr8 = adr_of home, adr_of [+4784] home, 0x0060, 0x3030
    call 10F20

tetromino_sprite:
    hex FF BD A5 A5 A5 A5 BD FF
    0x3030
    adr_of [-2] home
    sp = er6, pop er8

title_txt:
    str "TETRIS"
    hex 00

bottom_table:
    hex 00 2E
    adr_of [-2] reset_top
    hex 00 00
    adr_of [-2] loop
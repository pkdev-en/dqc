org 0xe9e0
er8:
    0xf039
print:
    xr0 = 0x0001, adr_of text
    printline
    er0 = 0x0011
    printline
    er0 = 0x0021
    printline
    er0 = 0x0031
    printline
    render.ddd4
scroll:
    er0 = 0x0500
    delay
    er2 = 0x0100
    [er8]+=er2,pop xr8
    0xf039
    0x3030
    er14 = adr_of [-2] scroll
    sp = er14, pop er14
text:
    str "aaaaaaaaaaaaaaaaabbbbbbbbbbbbbbbbbcccccccccccccccccddddddddddddddddd"
org 0xd180

#<48/34 bytes>
#pop xr0
#<dest> <addr bắt đầu của program>
#BL memcpy,pop er0
#<length full program>
#er14 = <dest> - 2
#sp = er14,pop er14


# 785c3130dee9600d3230
home:
#<48/34 bytes>
    er14 = 0xe9de  # <addr bắt đầu của program> - 2
    sp = er14,pop er14
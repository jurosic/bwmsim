buffer = []

def call(comp_dict):
    global buffer
    if 'ram' not in comp_dict.keys():
        raise ValueError("This simulation does not have a RAM component!")

    #check if flags are set
    flags = comp_dict['ram'].get_addresses((int("0x2012", 16), ))[0]

    if flags & 0b00000001:
        #dealing with int16

        mem = comp_dict['ram'].get_addresses((
                int("0x2010", 16),
                int("0x2011", 16)
            ))

        val = int(bin(mem[1])[2:].zfill(8) + bin(mem[0])[2:].zfill(8), 2)

        buffer.append(str(val))

        if flags & 0b10000000:
            #add newline
            buffer.append('\n')
        #reset flags
        comp_dict['ram'].set_address(int("0x2012", 16), 0)

    print("Text Buffer:")
    print(''.join(buffer))

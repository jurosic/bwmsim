text = []
buffer = []

first_call = True

def call(comp_dict):
    global text
    global buffer
    global first_call

    if 'ram' not in comp_dict.keys():
        raise ValueError("This simulation does not have a RAM component!")
    
    if first_call:
        #set values in memroy to avoid NoneType errors
        comp_dict['ram'].set_address(int("0x2020", 16), 0)
        comp_dict['ram'].set_address(int("0x2021", 16), 0)
        first_call = False


    #check if flags are set
    flags = comp_dict['ram'].get_addresses((int("0x2021", 16), ))[0]

    #flags:
    #set bit - flag
    #      0s - print rdy
    #      1s - char
    #      2u - int8
    #      2s - uint8
    #      3u - int16
    #      3s - uint16
    #      5s - \n
    #      6s - reverse (int to char covnersion)
    #      7s - EOF 

    #very cheesy thing, i dont feel like learning arrays yet
    if flags & 0b01000000:
        buffer.reverse()

    if flags == 0b00000011:
        #char
        mem = comp_dict['ram'].get_addresses((
                int("0x2020", 16), ))
        buffer.append(chr(mem[0]))
    elif flags == 0b00000001:
        #int8
        mem = comp_dict['ram'].get_addresses((
                int("0x2020", 16), ))
        buffer.append(str(to_signed_int8(mem[0])))
    elif flags == 0b00000101:
        #uint8 
        mem = comp_dict['ram'].get_addresses((
                int("0x2020", 16), ))
        buffer.append(str(mem[0]))
    elif flags == 0b00100000:
        buffer.append("\n")
    elif flags == 0b10000000:
        #eof
        text.extend(buffer)
        buffer = []


    #others TODO

    #reset flags
    comp_dict['ram'].set_address(int("0x2021", 16), 0)

    if text != []:
        print("Print Output:")
        print(''.join(text))

def to_signed_int8(val):
    val = val & 0xFF 
    
    if val > 127:
        return val - 256
    return val

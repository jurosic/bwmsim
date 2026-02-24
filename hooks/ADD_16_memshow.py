"""
    This hook shows the memory used by the ADD_16: SR
"""


def call(comp_dict):
    if "ram" not in comp_dict.keys():
        raise ValueError("This simulation does not contain a RAM component")

    addr = comp_dict['ram'].get_addresses((
        int("0x2000", 16),
        int("0x2001", 16),
        int("0x2002", 16),
        int("0x2003", 16)
        ))

    ma = bin(addr[1])[2:] + bin(addr[0])[2:]
    ta = bin(addr[3])[2:] + bin(addr[2])[2:]


    print('\n'.join((
        "ADD_16 UAD:",
        f"MLA: {addr[0]}",
        f"MHA: {addr[1]}",
        f"TLA: {addr[2]}",
        f"THA: {addr[3]}",

        f"MA IS: {int(ma, 2)}",
        f"TA IS: {int(ta, 2)}"
        )))


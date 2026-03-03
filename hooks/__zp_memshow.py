def call(comp_dict):
    if 'ram' not in comp_dict.keys():
        raise ValueError("This simulation does not contain a RAM component!")

    print("ZP:")
    comp_dict['ram'].show("0x0000", "0x0010")

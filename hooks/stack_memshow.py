def call(comp_dict):
    if "ram" not in comp_dict.keys():
        raise ValueError("This simulation does not have a RAM component!!")

    print("Stack:")
    comp_dict['ram'].show("0x01F0", "0x0200")


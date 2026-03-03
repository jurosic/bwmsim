def call(comp_dict):
    if 'ram' not in comp_dict.keys():
        raise ValueError("This simulation does not contain a RAM component!")

    print("DYN: ")
    #loop over all absolute addresses and check if theyre set to something
    for i, val in enumerate(comp_dict['ram']._memory):
        if val != None:
            print(f"{hex(i):>10}: {val:>10} {hex(val):>10}")

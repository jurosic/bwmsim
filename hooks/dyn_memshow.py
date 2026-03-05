dfs = {}

def call(comp_dict):
    global dfs

    if 'ram' not in comp_dict.keys():
        raise ValueError("This simulation does not contain a RAM component!")
    if 'debug_flags' not in comp_dict.keys():
        raise ValueError("This program does have debug flags!")

    print("DYN: ")

    MDE = 0

    if dfs == {}:
        with open(comp_dict['debug_flags'], "r") as f:
            for line in f:
                if line == ".begin CONSTANTS\n":
                    MDE = 0
                    continue
                if line == ".begin VARIABLES\n":
                    MDE = 1
                    continue
                if line == ".begin LABELS\n":
                    MDE = 2
                    continue

                #read constants
                match MDE:
                    case 0:
                        splt = line.split("-")
                        if splt[0].startswith('$'):
                            splt[0] = splt[0][1:]
                        dfs[splt[0]] = {"type": "con", "name": splt[1].strip()}
                    case 1:
                        splt = line.split(":")
                        addr = splt[0].strip("$")
                        dfs[addr] = {}
                        vals = splt[1].split(",")
                        
                        for val in vals:
                            val = val.split("-")
                            val[1] = val[1].strip('$')
                            dfs[addr][val[0]] = val[1].strip()
                        dfs[addr]["type"] = "var"

                        #add extensions
                        for i in range(1, int(dfs[addr]['size'])):
                            nxt = int(addr, 16) + i
                            dfs[f"0x{nxt:04X}"] = {"type": "ext", "who": addr}
                    case 2:
                        splt = line.split("-")
                        if splt[0].startswith('$'):
                            splt[0] = "0x" + splt[0][1:]
                        dfs[splt[0]] = {"type": "lab", "name": splt[1].strip()}
                        


    #loop over all absolute addresses and check if theyre set to something
    for i, val in enumerate(comp_dict['ram']._memory):
        if val != None:
            dbg = ""
            search = f"0x{i:04X}"
            if search in dfs.keys():
                dbg = dfs[search]
            if dbg == "":
                print(f"{hex(i):>10}: {val:>10} {hex(val):>10}")
                continue

            if dbg["type"] == "lab" or dbg["type"] == "con":
                print(f"{hex(i):>10}: {val:>10} {hex(val):>10} - {dbg['name']}")
            elif dbg["type"] == "var": 
                oval = val
                for j in range(1, int(dbg['size'])):
                    nval = comp_dict['ram']._memory[i+j]
                    if nval is not None:
                        nval = nval << j*8
                        val += nval
                print(f"{hex(i):>10}: {val:>10} {hex(val):>10} - {dbg['name']} - {oval}")
            elif dbg["type"] == "ext": 
                print(f"{hex(i):>10}: {val:>10} {hex(val):>10} - ^^")

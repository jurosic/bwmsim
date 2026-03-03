from libs.ele import Pin as EPin
from libs.ele import Group as EGroup


class AT28C256():
    def __init__(self):
        self.addr_bus = EGroup(15)
        self.io_bus   = EGroup(8)
        
        self.n_ce     = EPin()
        self.n_oe     = EPin()
        self.n_we     = EPin()
        
        self._memory = [None for _ in range(0, 32_768)]
        
    def debug(self):
        return {
            "io" : int(''.join(['1' if x else '0' for x in self.io_bus.state]),2),
            "ab" : int(''.join(['1' if x else '0' for x in self.addr_bus.state]),2),
            'n_ce' : self.n_ce.state,
            'n_oe' : self.n_oe.state,
            'n_we' : self.n_we.state
        }
        
    def print_dbg(self):
        dbg = self.debug()
        if self.n_ce.state:
            """print('\n'.join((
                "AT28C256 :",
                f"IOB :{dbg['io']:#010b} ({hex(dbg['io'])})",
                f"ADB :{dbg['ab']:#010b} ({hex(dbg['ab'])})",
                f"CE  :{dbg['n_ce']} ({not dbg['n_ce']})",
                f"OE  :{dbg['n_oe']} ({not dbg['n_oe']})",
                f"WE  :{dbg['n_we']} ({not dbg['n_we']})"
            )))"""
            print('\n'.join((
                "xxxAT28C256",
                f"IOB :{dbg['io']:#010b} ({hex(dbg['io'])})",
                f"ADB :{dbg['ab']:#010b} ({hex(dbg['ab'])})",
                )))
            return
        
        if not self.n_oe.state:
            """print('\n'.join((
                "AT28C256 :",
                f"IOB :{dbg['io']:#010b} ({hex(dbg['io'])})",
                f"ADB :{dbg['ab']:#010b} ({hex(dbg['ab'])})",
                f"CE  :{dbg['n_ce']} ({not dbg['n_ce']})",
                f"OE  :{dbg['n_oe']} ({not dbg['n_oe']})",
                f"WE  :{dbg['n_we']} ({not dbg['n_we']})"
            )))"""
            print('\n'.join((
                    "<--AT28C256",
                    f"IOB :{dbg['io']:#010b} ({hex(dbg['io'])})",
                    f"ADB :{dbg['ab']:#010b} ({hex(dbg['ab'])})",
                    )))
            return
        
    def update(self):
        if self.n_ce.state:
            return

        if not self.n_we.state:
            #todo?
            return

        if not self.n_oe.state:
            #decode address from addrpins
            addr = self.addr_bus.state
            addr = ['1' if x else '0' for x in addr]
            addr = ''.join(addr)
            addr = int(addr, 2)
            
            #get data at addr
            data = self._memory[addr]
            data = bin(data)[2:]
            data = [True if x == '1' else False for x in data]
            pad = [False for _ in range(8-len(data))]
            pad.extend(data)
            self.io_bus.signal(pad)

            
    def load(self, filename: str):
        #should be .bin files
        
        cnter = 0
        with open(filename, "rb") as f:
            while(byte := f.read(1)):
                self._memory[cnter] = int.from_bytes(byte)
                cnter+=1
                
if __name__ == "__main__":
    #test
    
    mem = AT28C256()
    
    mem.load('test.bin')
    
    mem.n_ce.signal(False)
    mem.n_oe.signal(False)
    
    addr = bin(4)
    addr = [True if x == '1' else False for x in addr]
    #pad >:(
    pad = [False for _ in range(0, 15-len(addr))]
    pad.extend(addr)
    
    print(pad)
    
    mem.addr_bus.signal(pad)
    
    mem.update()
    
    print(mem._memory[0:10])
    
    print(mem.io_bus.state)
    
    
    print("MEM DUMP")
    for i in range(0, 11):
        print(hex(mem._memory[i]))
        
    print()

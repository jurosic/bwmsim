from libs.ele import Group as EGroup
from libs.ele import Pin as EPin

class CY62256N:
    def __init__(self):
        self.addr_bus = EGroup(15)
        self.io_bus = EGroup(8)
        
        self.n_we = EPin()
        self.n_oe = EPin()
        self.n_ce = EPin()
        
        self._memory = [0 for _ in range(32_768)]
        
    def debug(self):
        return {
            "io" : int(''.join(['1' if x else '0' for x in self.io_bus.state]),2),
            "ab" : int(''.join(['1' if x else '0' for x in self.addr_bus.state]),2),
            'n_ce' : self.n_ce.state,
            'n_oe' : self.n_oe.state,
            'n_we' : self.n_we.state
        }
        
    def show(self, f, t):
        for i in range(int(f, 16), int(t, 16)):
            print(f"{i} - {self._memory[i]}")
        
    def update(self):
        if self.n_ce.state:
            dbg = self.debug()
            print('\n'.join((
                "CY62256N :",
                f"IOB :{dbg['io']:#010b} ({hex(dbg['io'])})",
                f"ADB :{dbg['ab']:#010b} ({hex(dbg['ab'])})",
                f"CE  :{dbg['n_ce']} ({not dbg['n_ce']})",
                f"OE  :{dbg['n_oe']} ({not dbg['n_oe']})",
                f"WE  :{dbg['n_we']} ({not dbg['n_we']})"
            )))
            return
        
        if not self.n_we.state:
            addr = self.addr_bus.state
            addr = ['1' if x else '0' for x in addr]
            addr = ''.join(addr)
            addr = int(addr, 2)
            
            data = self.io_bus.state
            data = ['1' if x else '0' for x in data]
            data = ''.join(data)
            data = int(data, 2)
            self._memory[addr] = data
            
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
            
        dbg = self.debug()
        print('\n'.join((
            "CY62256N :",
            f"IOB :{dbg['io']:#010b} ({hex(dbg['io'])})",
            f"ADB :{dbg['ab']:#010b} ({hex(dbg['ab'])})",
            f"CE  :{dbg['n_ce']} ({not dbg['n_ce']})",
            f"OE  :{dbg['n_oe']} ({not dbg['n_oe']})",
            f"WE  :{dbg['n_we']} ({not dbg['n_we']})"
        )))
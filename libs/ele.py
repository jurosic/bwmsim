class Pin():
    def __init__(self):
        self.connections = []
        self._state = False
       
    def connect(self, other: Pin, __neighbor: bool = True):
        if not isinstance(other, Pin):
            raise TypeError(f"{type(other)} is not of type pin")
        
        self.connections.append(other)
        if __neighbor:
            other.connect(self, False)

        
    def signal(self, signal: bool, __ignore: Pin = None):
        if not isinstance(signal, bool):
            raise TypeError(f"{type(signal)} is not of type bool")
        
        self._state = signal
        for pin in self.connections:
            #ignore makes sure we don't get stuck in an
            #infinite loop
            if pin == __ignore:
                continue
            pin.signal(signal, self)
            
    def traverse(self, nodes: list[Pin] = []):
        nodes.append(self)
        for pin in self.connections:
            if pin not in nodes:
                pin.traverse(nodes)
        
        return nodes
    
    @property
    def state(self):
        return self._state
    #tbi
    
class Group():
    def __init__(self, count):
        self.pins = []
        
        self.connections = [] #maybe useless?
        
        for _ in range(0, count):
            self.pins.append(Pin())
    
    def connect(self, other: Group, offset:int = 0, prange: list[int] = None, __neighbor: bool = True):
        if not isinstance(other, Group):
            raise TypeError(f"{type(other)} is not of type group")
        
        if not prange and len(self.pins) > len(other.pins):
            raise Warning(f"Pin count mismatch, no range specified, assuming 0-{len(other.pins)}")
        

        #exceptions very possible here
        self.connections.append(other)
        if __neighbor:
            a = prange[0] if prange else 0
            b = prange[1] if prange else len(self.pins)
   
            other.connect(self, offset, prange, False)
            for i in range(a, b):
                self.pins[i].connect(other.pins[i-offset])
            
    
    def signal(self, signal: list[bool], prange: tuple[int] = None, __ignore: Group = None):
        if not prange and len(signal) > len(self.pins):
            raise ValueError(f"Lenght of signal ({len(signal)}) is bigger than lenght of group ({len(self.pins)})")
        
        if prange and max(prange) > len(self.pins):
            raise ValueError(f"Value in range exceeds number of pins in group")
        
        if not all([isinstance(x, bool) for x in signal]):
            raise TypeError(f"Signal list contains non boolean value")
        
        
        a = prange[0] if prange else 0
        b = prange[1]+1 if prange else len(self.pins)
        if __ignore is not None:
            b = min(b, len(self.pins))
            
        
        #possible crash for len(signal) > paste
        for sig_i, pin_i in enumerate(range(a, b)):
            #print([a, b], pin_i, len(self.pins))
            self.pins[pin_i].signal(signal[sig_i], prange)
            
        
        #this might be redundant
        """for gp in self.connections:
            if __ignore == gp:
                continue
            #print("rec")
            gp.signal(signal, prange, self)
            #print("backrec")"""
            
    def traverse(self, nodes: list[Group] = []):
        nodes.append(self)
        for gp in self.connections:
            if gp not in nodes:
                gp.traverse(nodes)
                
        return nodes
    @property
    def state(self):
        return [x.state for x in self.pins]
    
class NOT:
    def __init__(self):
        self._in = Pin()
        self._out = Pin()
        
    def update(self):
        self._out.signal(not self._in.state)
            
    
if __name__ == "__main__":
    #tests
    p1 = Pin()
    p2 = Pin()
    p3 = Pin()
    p4 = Pin()
    
    p1.connect(p2)
    p3.connect(p2)
    p4.connect(p1)
    
    assert(p1.connections[0] == p2)
    assert(p2.connections[0] == p1)
    
    p1.signal(True)
    
    assert(p1.state == True)
    assert(p2.state == True)
    assert(p3.state == True)
    assert(p4.state == True)
    
    print(p1.traverse())
    
    """
        Groups
    """
    
    g1 = Group(4)
    g2 = Group(4)
    g3 = Group(4)
    
    g1.connect(g2)
    g3.connect(g2)
    
    assert(g1.connections[0] == g2)
    assert(g2.connections[0] == g1)
    
    g1.signal([True, False, False, True])
    print(g1.state)
    print(g3.state)

    assert(g3.state == [True, False, False, True])

    
    print(g1.traverse())
    
    
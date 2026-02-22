from libs.ele import Group as EGroup
from libs.ele import Pin as EPin
from libs.ele import NOT as ENOT

from chips.AT28C256 import AT28C256
from chips.SY6502 import SY6502
from chips.CY62256N import CY62256N

from sys import argv

rom = AT28C256()
ram = CY62256N()
cpu = SY6502()
mem_sw = ENOT()
rw_neg = ENOT()

def cb():
    mem_sw.update()
    rw_neg.update()
    rom.update()
    ram.update()

if __name__ == "__main__":

    rom.load(argv[1])


    cpu.addr_bus.connect(rom.addr_bus, 1, (1, 16))
    
    cpu.addr_bus.connect(ram.addr_bus, 1, (1, 16))

    assert(len(rom.addr_bus.connections) == 1)
    assert(len(ram.addr_bus.connections) == 1)

    cpu.data_bus.connect(rom.io_bus)
    cpu.data_bus.connect(ram.io_bus)
    assert(len(rom.io_bus.connections) == 1)
    assert(len(ram.io_bus.connections) == 1)
    
    cpu.addr_bus.pins[0].connect(ram.n_ce)
    cpu.addr_bus.pins[0].connect(mem_sw._in)
    rom.n_ce.connect(mem_sw._out)
    
    cpu.rw.connect(ram.n_we)
    cpu.rw.connect(rom.n_we)
    cpu.rw.connect(rw_neg._in)
    ram.n_oe.connect(rw_neg._out)
    rom.n_oe.connect(rw_neg._out)

    while cpu.run:
        cpu.update(cb)
        ram.show("0x01F0", "0x01FF")
        input()

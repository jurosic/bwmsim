from libs.ele import Pin as EPin
from libs.ele import Group as EGroup
from random import choice   

class SY6502():
    def __init__(self):
        #Meta flags
        self.run = True
        self.__cycles = 0
        
        #Registers
        #accumulator
        self.reg_ACC = EGroup(8)
        #norm registers
        self.reg_Y   = EGroup(8)
        self.reg_X   = EGroup(8)
        #address High/Low
        self.reg_PCH = EGroup(8)
        self.reg_PCL = EGroup(8)
        #start at FFFA? (main)
        self.reg_PCL.signal([True, True, True, True, True, False, True, False])
        self.reg_PCH.signal([True, True, True, True, True, True, True, True])
        #self.reg_PCL.signal([True for _ in range(0, 8)])
        #stackptr
        self.reg_S   = EGroup(8)
        self.reg_S.signal([True, True, True, True, True, True, True, True])
        #status reg
        self.reg_P   = EGroup(8)
        #reg_P needs to be random
        self.reg_P.signal([choice([True, False]) for _ in range(0, 8)])
        
        
        #Busses
        self.addr_bus = EGroup(16)
        self.data_bus = EGroup(8)
        
        #Pins
        self.rdy   = EPin()
        self.cout1 = EPin()
        self.cout1.signal(True)
        self.cout2 = EPin()
        self.cin1  = EPin()
        self.n_irq = EPin()
        self.n_nmi = EPin()
        self.sync  = EPin()
        self.n_res = EPin()
        self.rw    = EPin()
        
        self.instruction_set = {
            0x69: self._adc_i,
            0x6d: self._adc_a,
            0x65: self._adc_zp,
            0x29: self._and_i,
            0x2d: self._and_a,
            0x25: self._and_zp,
            0x65: self._adc_zp,
            0xf0: self._beq,
            0x30: self._bmi,
            0x10: self._bpl,
            0x00: self._brk,
            0x70: self._bvs,
            0x18: self._clc,
            0xd8: self._cld,
            0x58: self._cli,
            0x88: self._clv,
            0xc9: self._cmp_i,
            0xe0: self._cpx_i,
            0xc0: self._cpy_i,
            0x4c: self._jmp_a,
            0xa9: self._lda_i,
            0xa5: self._lda_zp,
            0xa2: self._ldx_i,
            0xa6: self._ldx_zp,
            0xa0: self._ldy_i,
            0x48: self._pha,
            0x68: self._pla,
            0x85: self._sta_zp,
            0x86: self._stx_zp,
            0xaa: self._tax,
            0xa8: self._tay,
            0x8a: self._txa,
            0x98: self._tya,
        }
        
    def get_debug(self):
        return  {
            "db" : int(''.join(['1' if x else '0' for x in self.data_bus.state]),2),
            "ab" : int(''.join(['1' if x else '0' for x in self.addr_bus.state]),2),
            "pch" : int(''.join(['1' if x else '0' for x in self.reg_PCH.state]),2),
            "pcl" : int(''.join(['1' if x else '0' for x in self.reg_PCL.state]),2),
            "acc" : int(''.join(['1' if x else '0' for x in self.reg_ACC.state]),2),
            "y" : int(''.join(['1' if x else '0' for x in self.reg_Y.state]),2),
            "x" : int(''.join(['1' if x else '0' for x in self.reg_X.state]),2),
            "p" : int(''.join(['1' if x else '0' for x in self.reg_P.state]),2),
            "s" : int(''.join(['1' if x else '0' for x in self.reg_S.state]),2),
            "rw" : self.rw.state
        }
        
    def _adc(self, val, reg_val):
        val = int(''.join(['1' if x else '0' for x in val]), 2)
        reg_val = int(''.join(['1' if x else '0' for x in reg_val]), 2)
        
        reg_val += val
        
        #simulate overflow
        if reg_val > 255:
            regp = self.reg_P.state
            regp[1] = True
            self.reg_P.signal(regp)
            reg_val -= 255
            
        reg_val = [True if x == '1' else False for x in bin(reg_val)[2:]]
        #paaaad :((
        pad = [False for _ in range(8-len(reg_val))]
        pad.extend(reg_val)
        
        self.reg_ACC.signal(pad)
        
    def _adc_i(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        self.rw.signal(True)
        
        ccb()
        
        val = self.data_bus.state.copy()
        reg_val = self.reg_ACC.state.copy()
        
        self._adc(val, reg_val)
        
    def _adc_zp(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        self.rw.signal(True)
        
        ccb()
        
        addr = self.data_bus.state.copy()
        #ppppadad
        pad = [False for _ in range(16-len(addr))]
        pad.extend(addr)
        self.addr_bus.signal(pad)
        
        ccb()
        
        val = self.data_bus.state.copy()
        reg_val = self.reg_ACC.state.copy()
        
        self._adc(val, reg_val)
        
    def _adc_a(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        self.rw.signal(True)

        ccb()

        addr1 = self.data_bus.state.copy()
        #ppppadad
        pad = [False for _ in range(16-len(addr1))]
        pad.extend(addr1)

        self.__increment_addr_reg()
        self.__push_addr_bus()

        ccb()

        addr2 = self.data_bus.state.copy()
        #ppppadad
        pad = [False for _ in range(16-len(addr2))]
        pad.extend(addr2)

        addr = []
        addr.extend(addr2)
        addr.extend(addr1)


        self.addr_bus.signal(addr)

        ccb()


        val = self.data_bus.state.copy()
        reg_val = self.reg_ACC.state.copy()

        self._adc(val, reg_val)

    def _and(self, val, reg_val):
        val = int(''.join(['1' if x else '0' for x in val]), 2)
        reg_val = int(''.join(['1' if x else '0' for x in reg_val]), 2)
        
        reg_val &= val
        
        reg_val = [True if x == '1' else False for x in bin(reg_val)[2:]]
        #paaaad :((
        pad = [False for _ in range(8-len(reg_val))]
        pad.extend(reg_val)
        
        self.reg_ACC.signal(pad)


    def _and_i(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        self.rw.signal(True)
        
        ccb()
        
        val = self.data_bus.state.copy()
        reg_val = self.reg_ACC.state.copy()
        
        self._and(val, reg_val)

    def _and_zp(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        self.rw.signal(True)
        
        ccb()
        
        addr = self.data_bus.state.copy()
        #ppppadad
        pad = [False for _ in range(16-len(addr))]
        pad.extend(addr)
        self.addr_bus.signal(pad)
        
        ccb()
        
        val = self.data_bus.state.copy()
        reg_val = self.reg_ACC.state.copy()
        
        self._and(val, reg_val)

    def _and_a(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        self.rw.signal(True)

        ccb()

        addr1 = self.data_bus.state.copy()
        #ppppadad
        pad = [False for _ in range(16-len(addr1))]
        pad.extend(addr1)

        self.__increment_addr_reg()
        self.__push_addr_bus()

        ccb()

        addr2 = self.data_bus.state.copy()
        #ppppadad
        pad = [False for _ in range(16-len(addr2))]
        pad.extend(addr2)

        addr = []
        addr.extend(addr2)
        addr.extend(addr1)


        self.addr_bus.signal(addr)

        ccb()


        val = self.data_bus.state.copy()
        reg_val = self.reg_ACC.state.copy()

        self._and(val, reg_val)


    def _beq(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        addr_offset = int(''.join(['1' if x else '0' for x in self.data_bus.state]), 2)
        
        regp = self.reg_P.state
        
        if regp[0] == False and regp[6] == True:
            self.__increment_addr_reg(addr_offset-1)
    
    def _bmi(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        addr_offset = self.data_bus.state.copy()
        addr_offset = int(''.join(['1' if x else '0' for x in addr_offset]), 2)


        regp = self.reg_P.state
        
        if regp[0] == True and regp[6] == False:
            self.__increment_addr_reg(addr_offset-1)
        
    def _bpl(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        addr_offset = self.data_bus.state.copy()
        addr_offset = int(''.join(['1' if x else '0' for x in addr_offset]), 2)
        
        regp = self.reg_P.state
        
        if regp[0] == False and regp[6] == False:
            self.__increment_addr_reg(addr_offset-1)
            
    def _bvs(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        addr_offset = self.data_bus.state.copy()
        addr_offset = int(''.join(['1' if x else '0' for x in addr_offset]), 2)
        
        regp = self.reg_P.state
        
        if regp[1] == True:
            self.__increment_addr_reg(addr_offset-1)
    
    def _brk(self, ccb):
        self.run = False
        
    def _clc(self, ccb):
        regp = self.reg_P.state
        regp[7] = False
        self.reg_P.signal(regp)
        
    def _cld(self, ccb):
        regp = self.reg_P.state
        regp[3] = False
        self.reg_P.signal(regp)
    def _cli(self, ccb):
        regp = self.reg_P.state
        regp[4] = False
        self.reg_P.signal(regp)
    def _clv(self, ccb):
        regp = self.reg_P.state
        regp[1] = False
        self.reg_P.signal(regp)
    
    def _cmp(self, val, reg_val):
        regp = self.reg_P.state
        if val > reg_val:
            regp[0] = False
            regp[6] = False
        
        if val == reg_val:
            regp[0] = False
            regp[6] = True
            
        if val < reg_val:
            regp[0] = True
            regp[6] = False
            
        self.reg_P.signal(regp)
        
    
    def _cmp_i(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        reg_val = ''.join(['1' if x else '0' for x in self.reg_ACC.state])
        reg_val = int(reg_val, 2)
        
        val = ''.join(['1' if x else '0' for x in self.data_bus.state])
        val = int(val, 2)
        
        self._cmp(val, reg_val)

    def _cpx_i(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        reg_val = ''.join(['1' if x else '0' for x in self.reg_X.state])
        reg_val = int(reg_val, 2)
        
        val = ''.join(['1' if x else '0' for x in self.data_bus.state])
        val = int(val, 2)
        
        self._cmp(val, reg_val)

    def _cpy_i(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        reg_val = ''.join(['1' if x else '0' for x in self.reg_Y.state])
        reg_val = int(reg_val, 2)
        
        val = ''.join(['1' if x else '0' for x in self.data_bus.state])
        val = int(val, 2)
        
        self._cmp(val, reg_val)

    def _jmp_a(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        first = self.data_bus.state.copy()
        
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        second = self.data_bus.state.copy()

        #subtract one for the increment at the end of the cycle
        #this is ugly but whatever
        whole = []
        whole.extend(second)
        whole.extend(first)
        whole = int(''.join(['1' if x else '0' for x in whole]), 2)
        whole -= 1
        whole = [True if x == '1' else False for x in bin(whole)[2:]]
        pad = [False for _ in range(16-len(whole))]
        pad.extend(whole)

        #split
        first = pad[8:16]
        second = pad[0:8]
        
        self.reg_PCL.signal(first)
        self.reg_PCH.signal(second)
        
    def _lda_i(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        #read data into ACC
        self.reg_ACC.signal(self.data_bus.state.copy())
        
    def _lda_zp(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        self.rw.signal(True)
        
        ccb()
        
        addr = self.data_bus.state.copy()
        #ppppadad
        pad = [False for _ in range(16-len(addr))]
        pad.extend(addr)
        self.addr_bus.signal(pad)
        ccb()
        self.reg_ACC.signal(self.data_bus.state.copy())
        
    def _ldx_i(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        #read data into ACC
        self.reg_X.signal(self.data_bus.state.copy())
        
    def _ldx_zp(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        self.rw.signal(True)
        
        ccb()
        
        addr = self.data_bus.state.copy()
        #ppppadad
        pad = [False for _ in range(16-len(addr))]
        pad.extend(addr)
        self.addr_bus.signal(pad)
        ccb()
        self.reg_X.signal(self.data_bus.state.copy())
        
    def _ldy_i(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        #read data into ACC
        self.reg_Y.signal(self.data_bus.state.copy())
        
    def _pha(self, ccb):
        sp = int(''.join('1' if x else '0' for x in self.reg_S.state), 2)
        addr = int("0x0100", 16) + sp
        addr = [True if x == '1' else False for x in bin(addr)[2:]]
        #papapapapapd
        pad = [False for _ in range(16-len(addr))]
        pad.extend(addr)
        self.addr_bus.signal(pad)
        
        sp -= 1
        sp = [True if x == '1' else False for x in bin(sp)[2:]]
        #pad... again :(
        pad = [False for _ in range(8-len(sp))]
        pad.extend(sp)
        self.reg_S.signal(pad)
        
        self.rw.signal(False)
        
        self.data_bus.signal(self.reg_ACC.state.copy())
        self.reg_ACC.signal([False for _ in range(8)])
        
        ccb()
        
        #leftover from not setting RW before
        self.rw.signal(True)
        
    def _pla(self, ccb):
        sp = int(''.join('1' if x else '0' for x in self.reg_S.state), 2)+1
        addr = int("0x0100", 16) + sp
        addr = [True if x == '1' else False for x in bin(addr)[2:]]
        #ppppp
        pad = [False for _ in range(16-len(addr))]
        pad.extend(addr)
        self.addr_bus.signal(pad)
        
        sp = [True if x == '1' else False for x in bin(sp)[2:]]
        #padpadpapda..
        pad = [False for _ in range(8-len(sp))]
        pad.extend(sp)
        
        self.reg_S.signal(pad)
        
        self.rw.signal(True)
        

        ccb()

        self.reg_ACC.signal(self.data_bus.state)
        
    def _sta_zp(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        self.rw.signal(True)
        
        ccb()
        
        self.rw.signal(False)
        addr = self.data_bus.state.copy()
        #ppppadad
        pad = [False for _ in range(16-len(addr))]
        pad.extend(addr)
        self.addr_bus.signal(pad)
        self.data_bus.signal(self.reg_ACC.state.copy())
        ccb()
        
        self.rw.signal(True)
        self.reg_ACC.signal([False for _ in range(8)])
        
    def _stx_zp(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        self.rw.signal(True)
        
        ccb()
        
        self.rw.signal(False)
        addr = self.data_bus.state.copy()
        #ppppadad
        pad = [False for _ in range(16-len(addr))]
        pad.extend(addr)
        self.addr_bus.signal(pad)
        self.data_bus.signal(self.reg_X.state.copy())
        ccb()
        
        self.rw.signal(True)
        self.reg_X.signal([False for _ in range(8)])
        
    def _tax(self, ccb):
        self.reg_X.signal(self.reg_ACC.state.copy())
        
    def _tay(self, ccb):
        self.reg_Y.signal(self.reg_ACC.state.copy())
        
    def _tsx(self, ccb):
        self.reg_X.signal(self.reg_S.state.copy())
        
    def _txa(self, ccb):
        self.reg_ACC.signal(self.reg_X.state.copy())
        
    def _txs(self, ccb):
        self.reg_S.signal(self.reg_X.state.copy())

    def _tya(self, ccb):
        self.reg_ACC.signal(self.reg_Y.state.copy())
        
        
    def __increment_addr_reg(self, offset: int = 1):
        pc = self.reg_PCH.state.copy()
        pc.extend(self.reg_PCL.state.copy())
        pc = int(''.join(['1' if x else '0' for x in pc]), 2)
        pc += offset
        pc = [True if x == '1' else False for x in bin(pc)[2:]]
        #:(( pad
        pad = [False for _ in range(16-len(pc))]
        pad.extend(pc)
        self.reg_PCH.signal(pad[:8])
        self.reg_PCL.signal(pad[8:16])
        
    def __push_addr_bus(self):
        self.addr_bus.signal(self.reg_PCH.state, (0, 7))
        self.addr_bus.signal(self.reg_PCL.state, (8, 15))
        
    def update(self, ccb):
        self.__cycles += 1
        
        self.cout1.signal(not self.cout1.state)
        self.cout2.signal(not self.cout1.state)
        
        """
            Guessing:
            1.1             set R
            1.2             set addr_bus
            1.3             set OE                  (ROM)(16th addr bit)
            1.4             read data_bus
            1.5             unset OE                (ROM)(16th addr bit)?
            1.6.1 (opt/arg) index reg_PCL, reg_PCH
            1.6.2 (opt/arg) set addr_bus
            1.7   (opt/arg) set OE                  (ROM)(16th addr bit)
            1.8   (opt/arg) read data_bus
            1.9             execute
            1.10            index reg_PCL, reg_PCH
            TBI write
            
        """
        print("="*20 + f"CYCLE: {self.__cycles}" + "="*20)
        
        self.rw.signal(True)
        self.__push_addr_bus()
        
        #call ccb
        ccb()
        
        inst = int(''.join(['1' if x else '0' for x in self.data_bus.state]), 2)
        mon = self.get_debug()
        
        
        print('\n'.join((
                "SY6502-INST :",
                f"DBS :{mon['db']:#010b} ({hex(mon['db'])})",
                f"PCL :{mon['pcl']:#010b} ({hex(mon['pcl'])})",
                f"PCH :{mon['pch']:#010b} ({hex(mon['pch'])})",
                f"ACC :{mon['acc']:#010b} ({hex(mon['acc'])})",
                f"X   :{mon['x']:#010b} ({hex(mon['x'])})",
                f"Y   :{mon['y']:#010b} ({hex(mon['y'])})",
                f"P   :{mon['p']:#010b} ({hex(mon['p'])})",
                f"S   :{mon['s']:#010b} ({hex(mon['s'])})",
                f"RW  :{mon['rw']}"
              )))
        
        
        if inst in self.instruction_set:
            self.instruction_set[inst](ccb)
        
        mon = self.get_debug()
        
        print('\n'.join((
                "SY6502-EXEC :",
                f"DBS :{mon['db']:#010b} ({hex(mon['db'])})",
                f"PCL :{mon['pcl']:#010b} ({hex(mon['pcl'])})",
                f"PCH :{mon['pch']:#010b} ({hex(mon['pch'])})",
                f"ACC :{mon['acc']:#010b} ({hex(mon['acc'])})",
                f"X   :{mon['x']:#010b} ({hex(mon['x'])})",
                f"Y   :{mon['y']:#010b} ({hex(mon['y'])})",
                f"P   :{mon['p']:#010b} ({hex(mon['p'])})",
                f"S   :{mon['s']:#010b} ({hex(mon['s'])})",
                f"RW  :{mon['rw']}"
              )))
        
        self.__increment_addr_reg()

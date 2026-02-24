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
        
        #Internal sinumation things
        self.__breaking = False

        self.instruction_set = {
            0x69: self._adc_i,
            0x6d: self._adc_a,
            0x65: self._adc_zp,
            0x29: self._and_i,
            0x2d: self._and_a,
            0x25: self._and_zp,
            0x0e: self._asl_a,
            0x06: self._asl_zp,
            0x90: self._bcc,
            0xb0: self._bcs,
            0xef: self._beq,
            0x2c: self._bit_a,
            0x24: self._bit_zp,
            0x30: self._bmi,
            0xd0: self._bne, 
            0x10: self._bpl,
            0x00: self._brk,
            0x50: self._bvc,
            0x70: self._bvs,
            0x18: self._clc,
            0xd8: self._cld,
            0x58: self._cli,
            0xB8: self._clv,
            0xc9: self._cmp_i,
            0xcd: self._cmp_a,
            0xc5: self._cmp_zp,
            0xe0: self._cpx_i,
            0xce: self._cpx_a,
            0xe4: self._cpx_zp,
            0xc0: self._cpy_i,
            0xcc: self._cpy_a,
            0xe4: self._cpy_zp,
            0xce: self._dec_a,
            0xc6: self._dec_zp,
            0x49: self._eor_i,
            0x4d: self._eor_a,
            0x45: self._eor_zp,
            0xee: self._inc_a,
            0xe6: self._inc_zp,
            0x4c: self._jmp_a,
            0x20: self._jsr_a,
            0xa9: self._lda_i,
            0xad: self._lda_a,
            0xa5: self._lda_zp,
            0xa2: self._ldx_i,
            0xae: self._ldx_a,
            0xa6: self._ldx_zp,
            0xa0: self._ldy_i,
            0xac: self._ldy_a,
            0xa4: self._ldy_zp,
            0x4e: self._lsr_a,
            0x46: self._lsr_zp,
            0xea: self._nop,
            0x09: self._ora_i,
            0x0d: self._ora_a,
            0x05: self._ora_zp,
            0x48: self._pha,
            0x08: self._php,
            0x68: self._pla,
            0x28: self._plp,
            0x2e: self._rol_a,
            0x26: self._rol_zp,
            0x6e: self._ror_a,
            0x66: self._ror_zp,
            0x40: self._rti,
            0x60: self._rts,
            0xe9: self._sbc_i,
            0xed: self._sbc_a,
            0xe5: self._sbc_zp,
            0x38: self._sec,
            0xf8: self._sed,
            0x78: self._sei,
            0x8d: self._sta_a,
            0x85: self._sta_zp,
            0x8e: self._stx_a,
            0x86: self._stx_zp,
            0x8c: self._sty_a,
            0x84: self._sty_zp,
            0xaa: self._tax,
            0xa8: self._tay,
            0xba: self._tsx,
            0x8a: self._txa,
            0x9a: self._txs,
            0x98: self._tya,
            
            #very very special breakpoint instruction (ultra rare ;))
            0x67: self._brpnt,
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
        carry = 1 if self.reg_P.state[7] else 0
        val_int = int(''.join(['1' if x else '0' for x in val]), 2)
        acc_int = int(''.join(['1' if x else '0' for x in reg_val]), 2)
        
        res = acc_int + val_int + carry
        
        regp = self.reg_P.state
        
        regp[7] = res > 255
        
        regp[6] = (res & 0xFF) == 0
        
        regp[1] = bool((acc_int ^ res) & (val_int ^ res) & 0x80)
        regp[0] = bool(res & 0x80)

        self.reg_P.signal(regp)
        
        res &= 0xFF
        
        res_bin_str = bin(res)[2:].zfill(8)
        pad = [True if x == '1' else False for x in res_bin_str]
        
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

    def _asl(self, val):
        #this one makes me want to refractor the whole code
        val = int(''.join(['1' if x else '0' for x in val]), 2)
        
        regp = self.reg_P.state
        regp[7] = bool(val & 0b10000000)
        #update zero and negative flags
        regp[6] = val == 0
        regp[0] = bool((val << 1) & 0b10000000)
        self.reg_P.signal(regp)
        
        val <<= 1
        val &= 0b11111111
        
        val = [True if x == '1' else False for x in bin(val)[2:]]
        #paaaad :((
        pad = [False for _ in range(8-len(val))]
        pad.extend(val)
        
        return pad

    def _asl_a(self, ccb):
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

        res = self._asl(val)
        
        self.data_bus.signal(res)

        self.rw.signal(False)
        ccb()
        self.rw.signal(True)

    def _asl_zp(self, ccb):
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

        res = self._asl(val)
        
        self.data_bus.signal(res)

        self.rw.signal(False)
        ccb()
        self.rw.signal(True)


    def _bcc(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        addr_offset = self.data_bus.state.copy()
        addr_offset = int(''.join(['1' if x else '0' for x in addr_offset]), 2)
        if addr_offset > 127:
            addr_offset -= 256
        
        regp = self.reg_P.state
        
        if regp[7] == False:
            self.__increment_addr_reg(addr_offset)        

    def _bcs(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        addr_offset = self.data_bus.state.copy()
        addr_offset = int(''.join(['1' if x else '0' for x in addr_offset]), 2)
        if addr_offset > 127:
            addr_offset -= 256
        
        regp = self.reg_P.state
        
        if regp[7] == True:
            self.__increment_addr_reg(addr_offset)        

    def _beq(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        addr_offset = int(''.join(['1' if x else '0' for x in self.data_bus.state]), 2)
        if addr_offset > 127:
            addr_offset -= 256
        
        regp = self.reg_P.state
        
        if regp[0] == False and regp[6] == True:
            self.__increment_addr_reg(addr_offset-1)
            
    def _bit(self, val): 
        val = int(''.join(['1' if x else '0' for x in val]), 2)
        
        regp = self.reg_P.state
        regp[0] = bool(val & 0b10000000)
        regp[1] = bool(val & 0b01000000)
        regp[6] = bool(val & 0b00000001)
        self.reg_P.signal(regp)

    def _bit_a(self, ccb):
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

        self._bit(val)

    def _bit_zp(self, ccb):
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

        self._bit(val)

   
    def _bmi(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        addr_offset = self.data_bus.state.copy()
        addr_offset = int(''.join(['1' if x else '0' for x in addr_offset]), 2)
        if addr_offset > 127:
            addr_offset -= 256


        regp = self.reg_P.state
        
        if regp[0] == True:
            self.__increment_addr_reg(addr_offset)
        
    def _bpl(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        addr_offset = self.data_bus.state.copy()
        addr_offset = int(''.join(['1' if x else '0' for x in addr_offset]), 2)
        if addr_offset > 127:
            addr_offset -= 256
        
        regp = self.reg_P.state
        
        if regp[0] == False: 
            self.__increment_addr_reg(addr_offset)

    def _bne(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        addr_offset = self.data_bus.state.copy()
        addr_offset = int(''.join(['1' if x else '0' for x in addr_offset]), 2)
        if addr_offset > 127:
            addr_offset -= 256
        
        regp = self.reg_P.state
        
        if regp[6] == False:
            self.__increment_addr_reg(addr_offset)        
        
    def _brk(self, ccb):
        self.run = False

    def _bvc(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        addr_offset = self.data_bus.state.copy()
        addr_offset = int(''.join(['1' if x else '0' for x in addr_offset]), 2)
        if addr_offset > 127:
            addr_offset -= 256

        regp = self.reg_P.state
        
        if regp[1] == False:
            self.__increment_addr_reg(addr_offset)

    def _bvs(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        addr_offset = self.data_bus.state.copy()
        addr_offset = int(''.join(['1' if x else '0' for x in addr_offset]), 2)
        if addr_offset > 127:
            addr_offset -= 256

        regp = self.reg_P.state
        
        if regp[1] == True:
            self.__increment_addr_reg(addr_offset)

        
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
        if reg_val > val:
            regp[0] = False
            regp[6] = False
        
        if val == reg_val:
            regp[0] = False
            regp[6] = True
            
        if reg_val < val:
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

    def _cmp_a(self, ccb):
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

        self._cmp(val, reg_val)

    def _cmp_zp(self, ccb):
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
        
        self._cmp(val, reg_val)

    def _cpx(self, val, reg_val):
        regp = self.reg_P.state
        if reg_val > val:
            regp[0] = False
            regp[6] = False
        
        if val == reg_val:
            regp[0] = False
            regp[6] = True
            
        if reg_val < val:
            regp[0] = True
            regp[6] = False
            
        self.reg_P.signal(regp)

    def _cpx_i(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        reg_val = ''.join(['1' if x else '0' for x in self.reg_X.state])
        reg_val = int(reg_val, 2)
        
        val = ''.join(['1' if x else '0' for x in self.data_bus.state])
        val = int(val, 2)
        
        self._cpx(val, reg_val)

    def _cpx_a(self, ccb):
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
        reg_val = self.reg_X.state.copy()

        self._cpx(val, reg_val)

    def _cpx_zp(self, ccb):
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
        reg_val = self.reg_X.state.copy()
        
        self._cpx(val, reg_val)

    def _cpy(self, val, reg_val):
        regp = self.reg_P.state
        if reg_val > val:
            regp[0] = False
            regp[6] = False
        
        if val == reg_val:
            regp[0] = False
            regp[6] = True
            
        if reg_val < val:
            regp[0] = True
            regp[6] = False
            
        self.reg_P.signal(regp)

    def _cpy_i(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        reg_val = ''.join(['1' if x else '0' for x in self.reg_Y.state])
        reg_val = int(reg_val, 2)
        
        val = ''.join(['1' if x else '0' for x in self.data_bus.state])
        val = int(val, 2)
        
        self._cpy(val, reg_val)

    def _cpy_a(self, ccb):
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
        reg_val = self.reg_Y.state.copy()

        self._cpy(val, reg_val)

    def _cpy_zp(self, ccb):
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
        reg_val = self.reg_Y.state.copy()
        
        self._cpy(val, reg_val)

    def _dec(self, val):
        val = int(''.join(['1' if x else '0' for x in val]), 2)
        
        val -= 1
        val &= 0b11111111
       
        #update zero and negative flags
        regp = self.reg_P.state
        regp[6] = val == 0
        regp[0] = bool(val & 0b10000000)
        self.reg_P.signal(regp)

        val = [True if x == '1' else False for x in bin(val)[2:]]
        #paaaad :((
        pad = [False for _ in range(8-len(val))]
        pad.extend(val)
        
        return pad

    def _dec_a(self, ccb):
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

        res = self._dec(val)
        
        self.data_bus.signal(res)

        self.rw.signal(False)
        ccb()
        self.rw.signal(True)

    def _dec_zp(self, ccb):
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

        res = self._dec(val)
        
        self.data_bus.signal(res)

        self.rw.signal(False)
        ccb()
        self.rw.signal(True)

    def _eor(self, val, reg_val): 
        val = int(''.join(['1' if x else '0' for x in val]), 2)
        reg_val = int(''.join(['1' if x else '0' for x in reg_val]), 2)
        
        reg_val ^= val
        
        reg_val = [True if x == '1' else False for x in bin(reg_val)[2:]]
        #paaaad :((
        pad = [False for _ in range(8-len(reg_val))]
        pad.extend(reg_val)
        
        self.reg_ACC.signal(pad)

    def _eor_i(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        self.rw.signal(True)
        
        ccb()
        
        val = self.data_bus.state.copy()
        reg_val = self.reg_ACC.state.copy()
        
        self._eor(val, reg_val)

    def _eor_zp(self, ccb):
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
        
        self._eor(val, reg_val)

    def _eor_a(self, ccb):
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

        self._eor(val, reg_val)

    def _inc(self, val):
        val = int(''.join(['1' if x else '0' for x in val]), 2)
        
        val += 1
        val &= 0b11111111

        #update zero and negative flags
        regp = self.reg_P.state
        regp[6] = val == 0
        regp[0] = bool(val & 0b10000000)
        self.reg_P.signal(regp)
        
        val = [True if x == '1' else False for x in bin(val)[2:]]
        #paaaad :((
        pad = [False for _ in range(8-len(val))]
        pad.extend(val)
        
        return pad

    def _inc_a(self, ccb):
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

        res = self._inc(val)
        
        self.data_bus.signal(res)

        self.rw.signal(False)
        ccb()
        self.rw.signal(True)

    def _inc_zp(self, ccb):
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

        res = self._inc(val)
        
        self.data_bus.signal(res)

        self.rw.signal(False)
        ccb()
        self.rw.signal(True)

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

    def _jsr_a(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        ccb()
        addr_low = self.data_bus.state.copy()

        self.__increment_addr_reg()
        self.__push_addr_bus()
        ccb()
        addr_high = self.data_bus.state.copy()

        sp = int(''.join(['1' if x else '0' for x in self.reg_S.state]), 2)

        stack_addr_high = 0x0100 + sp
        stack_addr_high_bin = [True if x == '1' else False for x in bin(stack_addr_high)[2:].zfill(16)]
        
        self.addr_bus.signal(stack_addr_high_bin)
        self.data_bus.signal(self.reg_PCH.state.copy())
        self.rw.signal(False)
        ccb()
        
        sp = (sp - 1) & 0xFF

        stack_addr_low = 0x0100 + sp
        stack_addr_low_bin = [True if x == '1' else False for x in bin(stack_addr_low)[2:].zfill(16)]
        
        self.addr_bus.signal(stack_addr_low_bin)
        self.data_bus.signal(self.reg_PCL.state.copy())
        self.rw.signal(False)
        ccb()
        
        sp = (sp - 1) & 0xFF 

        sp_bin = [True if x == '1' else False for x in bin(sp)[2:].zfill(8)]
        self.reg_S.signal(sp_bin)
        
        self.rw.signal(True)

        self.reg_PCL.signal(addr_low)
        self.reg_PCH.signal(addr_high)

        #cheeky ;)
        self.__increment_addr_reg(-1)

    def _lda_i(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        #read data into ACC
        self.reg_ACC.signal(self.data_bus.state.copy())

        #reset regp
        regp = self.reg_P.state
        regp[0] = self.reg_ACC.state[7] #negative flag
        regp[1] = self.reg_ACC.state == [False for _ in range(8)] #zero flag
        self.reg_P.signal(regp)

    def _lda_a(self, ccb):
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

        self.reg_ACC.signal(self.data_bus.state.copy())

        #reset regp
        regp = self.reg_P.state
        regp[0] = self.reg_ACC.state[7] #negative flag
        regp[1] = self.reg_ACC.state == [False for _ in range(8)] #zero flag
        self.reg_P.signal(regp)
        
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

        #reset regp
        regp = self.reg_P.state
        regp[0] = self.reg_ACC.state[7] #negative flag
        regp[1] = self.reg_ACC.state == [False for _ in range(8)] #zero flag
        self.reg_P.signal(regp)
        
    def _ldx_i(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        
        ccb()
        
        self.reg_X.signal(self.data_bus.state.copy())

    def _ldx_a(self, ccb):
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

    def _ldy_a(self, ccb):
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

        self.reg_Y.signal(self.data_bus.state.copy())

    def _ldy_zp(self, ccb):
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
        self.reg_Y.signal(self.data_bus.state.copy())

    def _lsr(self, val):
        val = int(''.join(['1' if x else '0' for x in val]), 2)
        
        regp = self.reg_P.state
        regp[7] = bool(val & 0b00000001)
        self.reg_P.signal(regp)
        
        val >>= 1
        
        val = [True if x == '1' else False for x in bin(val)[2:]]
        #paaaad :((
        pad = [False for _ in range(8-len(val))]
        pad.extend(val)
        
        return pad

    def _lsr_a(self, ccb):
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

        res = self._lsr(val)
        
        self.data_bus.signal(res)

        self.rw.signal(False)
        ccb()
        self.rw.signal(True)

    def _lsr_zp(self, ccb):
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

        res = self._lsr(val)
        
        self.data_bus.signal(res)

        self.rw.signal(False)
        ccb()
        self.rw.signal(True)

    def _nop(self, ccb):
        pass #lol

    def _ora(self, val, reg_val): 
        val = int(''.join(['1' if x else '0' for x in val]), 2)
        reg_val = int(''.join(['1' if x else '0' for x in reg_val]), 2)
        
        reg_val |= val
        
        reg_val = [True if x == '1' else False for x in bin(reg_val)[2:]]
        #paaaad :((
        pad = [False for _ in range(8-len(reg_val))]
        pad.extend(reg_val)
        
        self.reg_ACC.signal(pad)

    def _ora_i(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        self.rw.signal(True)
        
        ccb()
        
        val = self.data_bus.state.copy()
        reg_val = self.reg_ACC.state.copy()
        
        self._ora(val, reg_val)

    def _ora_a(self, ccb):
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

        self._ora(val, reg_val)

    def _ora_zp(self, ccb):
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
        
        self._ora(val, reg_val)

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
        #self.reg_ACC.signal([False for _ in range(8)])
        
        ccb()
        
        #leftover from not setting RW before
        self.rw.signal(True)

    def _php(self, ccb):
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
        
        self.data_bus.signal(self.reg_P.state.copy())
        
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

    def _plp(self, ccb):
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

        self.reg_P.signal(self.data_bus.state)

    def _rol(self, val):
        bb = val[0] #bit that will be rotated around

        regp = self.reg_P.state
        val.pop(0)
        val.append(regp[7]) #carry flag
        regp[7] = bb #carry flag

        #update other flags
        #zero flag
        regp[6] = val == [False for _ in range(8)]
        #negative flag
        regp[0] = val[7]

        self.reg_P.signal(regp)

        return val

    def _rol_a(self, ccb):
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

        res = self._rol(val)
        
        self.data_bus.signal(res)

        self.rw.signal(False)
        ccb()
        self.rw.signal(True)

    def _rol_zp(self, ccb):
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

        res = self._rol(val)
        
        self.data_bus.signal(res)

        self.rw.signal(False)
        ccb()
        self.rw.signal(True)

    def _ror(self, val):
        bb = val[7] #bit that will be rotated around

        regp = self.reg_P.state
        val.pop()
        val.insert(0, bb)
        regp[7] = bb #carry flag
        self.reg_P.signal(regp)

        return val

    def _ror_a(self, ccb):
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

        res = self._ror(val)
        
        self.data_bus.signal(res)

        self.rw.signal(False)
        ccb()
        self.rw.signal(True)

    def _ror_zp(self, ccb): 
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

        res = self._ror(val)
        
        self.data_bus.signal(res)

        self.rw.signal(False)
        ccb()
        self.rw.signal(True)

    def _rti(self, ccb):
        raise NotImplementedError("RTI not implemented yet") #TODO

    def _rts(self, ccb): 
        # 1. Dummy read (the 6502 hardware requires this clock cycle)
        self.__increment_addr_reg()
        self.__push_addr_bus()
        ccb()

        # 2. Get current Stack Pointer
        sp = int(''.join(['1' if x else '0' for x in self.reg_S.state]), 2)

        # 3. Pull PCL from Stack
        sp = (sp + 1) & 0xFF
        stack_addr_low = 0x0100 + sp
        self.addr_bus.signal([True if x == '1' else False for x in bin(stack_addr_low)[2:].zfill(16)])
        ccb()
        addr_low = self.data_bus.state.copy()

        # 4. Pull PCH from Stack
        sp = (sp + 1) & 0xFF
        stack_addr_high = 0x0100 + sp
        self.addr_bus.signal([True if x == '1' else False for x in bin(stack_addr_high)[2:].zfill(16)])
        ccb()
        addr_high = self.data_bus.state.copy()

        # 5. Save updated Stack Pointer
        self.reg_S.signal([True if x == '1' else False for x in bin(sp)[2:].zfill(8)])

        # 6. Restore the Program Counter!
        # Because your JSR correctly pushed Target - 1 (0x8010), 
        # and your engine pre-increments before the next fetch, 
        # setting it to exactly what we pulled will perfectly land on 0x8011!
        self.reg_PCL.signal(addr_low)
        self.reg_PCH.signal(addr_high)

    def _sbc(self, val, reg_val):
        val = int(''.join(['1' if x else '0' for x in val]), 2)
        reg_val = int(''.join(['1' if x else '0' for x in reg_val]), 2)
        
        regp = self.reg_P.state
        if not regp[0]: #if carry is clear, subtract one more
            val += 1
        
        reg_val -= val
        
        reg_val &= 0b11111111
        
        reg_val = [True if x == '1' else False for x in bin(reg_val)[2:]]
        #paaaad :((
        pad = [False for _ in range(8-len(reg_val))]
        pad.extend(reg_val)
        
        self.reg_ACC.signal(pad)

    def _sbc_i(self, ccb):
        self.__increment_addr_reg()
        self.__push_addr_bus()
        self.rw.signal(True)
        
        ccb()
        
        val = self.data_bus.state.copy()
        reg_val = self.reg_ACC.state.copy()
        
        self._sbc(val, reg_val)

    def _sbc_a(self, ccb):
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

        self._sbc(val, reg_val)

    def _sbc_zp(self, ccb):
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
        
        self._sbc(val, reg_val)

    def _sec(self, ccb):
        regp = self.reg_P.state
        regp[0] = True
        self.reg_P.signal(regp)

    def _sed(self, ccb):
        regp = self.reg_P.state
        regp[3] = True
        self.reg_P.signal(regp)

    def _sei(self, ccb):
        regp = self.reg_P.state
        regp[2] = True
        self.reg_P.signal(regp)

    def _sta_a(self, ccb):
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


        self.rw.signal(False)
        
        self.data_bus.signal(self.reg_ACC.state.copy())
        
        ccb()
        
        self.rw.signal(True)
        
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

    def _stx_a(self, ccb):
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


        self.rw.signal(False)
        
        self.data_bus.signal(self.reg_X.state.copy())
        
        ccb()
        
        self.rw.signal(True)
        
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

    def _sty_a(self, ccb):
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


        self.rw.signal(False)
        
        self.data_bus.signal(self.reg_Y.state.copy())
        
        ccb()
        
        self.rw.signal(True)

    def _sty_zp(self, ccb):
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
        self.data_bus.signal(self.reg_Y.state.copy())
        ccb()
        
        self.rw.signal(True)
        
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

    def _brpnt(self, ccb):
        #breakpoint instruction
        self.__breaking = not self.__breaking
        
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

        if self.__breaking:
            input()

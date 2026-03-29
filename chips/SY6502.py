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
        #stackptr
        self.reg_S   = EGroup(8)
        self.reg_S.signal([True, True, True, True, True, True, True, True])
        #status reg
        self.reg_P   = EGroup(8)
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
        
        self._breaking = False

        self.instruction_set = {
            0x69: self._adc_i,  0x6d: self._adc_a,  0x65: self._adc_zp, 0x61: self._adc_ix,
            0x71: self._adc_iy, 0x75: self._adc_zpx,0x7d: self._adc_ax, 0x79: self._adc_ay,
            0x29: self._and_i,  0x2d: self._and_a,  0x25: self._and_zp, 0x21: self._and_ix,
            0x31: self._and_iy, 0x35: self._and_zpx,0x3d: self._and_ax, 0x39: self._and_ay,
            0x0e: self._asl_a,  0x06: self._asl_zp, 0x0a: self._asl_acc,0x16: self._asl_zpx,
            0x1e: self._asl_ax, 0x90: self._bcc,    0xb0: self._bcs,    0xef: self._beq,
            0x2c: self._bit_a,  0x24: self._bit_zp, 0x30: self._bmi,    0xd0: self._bne, 
            0x10: self._bpl,    0x00: self._brk,    0x50: self._bvc,    0x70: self._bvs,
            0x18: self._clc,    0xd8: self._cld,    0x58: self._cli,    0xB8: self._clv,
            0xc9: self._cmp_i,  0xcd: self._cmp_a,  0xc5: self._cmp_zp, 0xc1: self._cmp_ix,
            0xd1: self._cmp_iy, 0xd5: self._cmp_zpx,0xdd: self._cmp_ax, 0xd9: self._cmp_ay,
            0xe0: self._cpx_i,  0xce: self._cpx_a,  0xe4: self._cpx_zp, 0xc0: self._cpy_i,
            0xcc: self._cpy_a,  0xe4: self._cpy_zp, 0xce: self._dec_a,  0xc6: self._dec_zp,
            0xd6: self._dec_zpx,0xde: self._dec_ax, 0xca: self._dex,    0x88: self._dey,
            0x49: self._eor_i,  0x4d: self._eor_a,  0x45: self._eor_zp, 0x41: self._eor_ix,
            0x51: self._eor_iy, 0x55: self._eor_zpx,0x5d: self._eor_ax, 0x59: self._eor_ay,
            0xee: self._inc_a,  0xe6: self._inc_zp, 0xf6: self._inc_zpx,0xfe: self._inc_ax,
            0xe8: self._inx,    0xc8: self._iny,    0x4c: self._jmp_a,  0x6c: self._jmp_ind,
            0x20: self._jsr_a,  0xa9: self._lda_i,  0xad: self._lda_a,  0xa5: self._lda_zp,
            0xa1: self._lda_ix, 0xb1: self._lda_iy, 0xb5: self._lda_zpx,0xbd: self._lda_ax,
            0xb9: self._lda_ay, 0xa2: self._ldx_i,  0xae: self._ldx_a,  0xa6: self._ldx_zp,
            0xbe: self._ldx_ay, 0xb6: self._ldx_zpy,0xa0: self._ldy_i,  0xac: self._ldy_a,
            0xa4: self._ldy_zp, 0xb4: self._ldy_zpx,0xbc: self._ldy_ax, 0x4e: self._lsr_a,
            0x46: self._lsr_zp, 0x4a: self._lsr_acc,0x56: self._lsr_zpx,0x5e: self._lsr_ax,
            0xea: self._nop,    0x09: self._ora_i,  0x0d: self._ora_a,  0x05: self._ora_zp,
            0x01: self._ora_ix, 0x11: self._ora_iy, 0x15: self._ora_zpx,0x1d: self._ora_ax,
            0x19: self._ora_ay, 0x48: self._pha,    0x08: self._php,    0x68: self._pla,
            0x28: self._plp,    0x2e: self._rol_a,  0x26: self._rol_zp, 0x2a: self._rol_acc,
            0x36: self._rol_zpx,0x3e: self._rol_ax, 0x6e: self._ror_a,  0x66: self._ror_zp,
            0x6a: self._ror_acc,0x76: self._ror_zpx,0x7e: self._ror_ax, 0x40: self._rti,
            0x60: self._rts,    0xe9: self._sbc_i,  0xed: self._sbc_a,  0xe5: self._sbc_zp,
            0xe1: self._sbc_ix, 0xf1: self._sbc_iy, 0xf5: self._sbc_zpx,0xfd: self._sbc_ax,
            0xf9: self._sbc_ay, 0x38: self._sec,    0xf8: self._sed,    0x78: self._sei,
            0x8d: self._sta_a,  0x85: self._sta_zp, 0x81: self._sta_ix, 0x91: self._sta_iy,
            0x95: self._sta_zpx,0x9d: self._sta_ax, 0x99: self._sta_ay, 0x8e: self._stx_a,
            0x86: self._stx_zp, 0x96: self._stx_zpy,0x8c: self._sty_a,  0x84: self._sty_zp,
            0x94: self._sty_zpx,0xaa: self._tax,    0xa8: self._tay,    0xba: self._tsx,
            0x8a: self._txa,    0x9a: self._txs,    0x98: self._tya,    0x67: self._brpnt,
        }

    # ========================== UTIL ==========================

    def _to_int(self, state_list): 
        return int(''.join(['1' if x else '0' for x in state_list]), 2)
    def _to_bits(self, val, length): 
        return [True if x == '1' else False for x in bin(val & ((1 << length) - 1))[2:].zfill(length)]

    def get_debug(self):
        return { "db": self._to_int(self.data_bus.state), 
                "ab": self._to_int(self.addr_bus.state), 
                "pch": self._to_int(self.reg_PCH.state), 
                "pcl": self._to_int(self.reg_PCL.state),
                "acc": self._to_int(self.reg_ACC.state), 
                "y": self._to_int(self.reg_Y.state),
                "x": self._to_int(self.reg_X.state), 
                "p": self._to_int(self.reg_P.state), 
                "s": self._to_int(self.reg_S.state), 
                "rw": self.rw.state 
        }

    def __increment_addr_reg(self, offset: int = 1):
        """Increments the address register with supplied offset

        Args:
            offset (int, optional): Ammount to offset by. Defaults to 1.
        """
        
        pc = self._to_int(self.reg_PCH.state + self.reg_PCL.state) + offset
        new_pc = self._to_bits(pc, 16)
        
        self.reg_PCH.signal(new_pc[:8])
        self.reg_PCL.signal(new_pc[8:16])
        
    def __push_addr_bus(self):
        """Pushes the PCH and PCL registers onto the address pins"""
        
        self.addr_bus.signal(self.reg_PCH.state, (0, 7))
        self.addr_bus.signal(self.reg_PCL.state, (8, 15))

    # ========================== STACK ==========================

    def _push_stack(self, ccb, val):
        """Pushes the supplied value onto stack

        Args:
            ccb (function): Callback to tick the connected components
            val (int): Value to be pushed
        """
        
        sp = self._to_int(self.reg_S.state)
        self.addr_bus.signal(self._to_bits(0x0100 + sp, 16))
        self.reg_S.signal(self._to_bits(sp - 1, 8))
        self.rw.signal(False)
        self.data_bus.signal(val)
        ccb()
        self.rw.signal(True)

    def _pop_stack(self, ccb):
        """Pops value from stack

        Args:
            ccb (function): Callback to tick the connected components

        Returns:
            int: Value popped from stack
        """
        
        sp = (self._to_int(self.reg_S.state) + 1) & 0xFF
        self.addr_bus.signal(self._to_bits(0x0100 + sp, 16))
        self.reg_S.signal(self._to_bits(sp, 8))
        self.rw.signal(True)
        ccb()
        return self.data_bus.state.copy()

    # ========================== ADDR MODES ==========================

    def _calc_addr_imm(self, ccb):
        """Steps the address registers over to the (next) immediate value

        Args:
            ccb (function): Callback function (unused)
        """
        
        self.__increment_addr_reg(); self.__push_addr_bus(); self.rw.signal(True)

    def _calc_addr_zp(self, ccb):
        """Steps the address registers over to the zeropage address specified by argument

        Args:
            ccb (function): Callback function to tick components
        """
        
        self.__increment_addr_reg(); self.__push_addr_bus(); self.rw.signal(True); ccb()
        self.addr_bus.signal([False for _ in range(8)] + self.data_bus.state.copy())

    def _calc_addr_abs(self, ccb):
        """Steps the address registers over to the absolute address specified by argument

        Args:
            ccb (function): Callback function to tick components
        """
        
        self.__increment_addr_reg(); self.__push_addr_bus(); self.rw.signal(True); ccb()
        addr_low = self.data_bus.state.copy()
        self.__increment_addr_reg(); self.__push_addr_bus(); ccb()
        self.addr_bus.signal(self.data_bus.state.copy() + addr_low)

    def _calc_addr_zpx(self, ccb):
        """Steps the address registers over to the zeropage address indexed by X 

        Args:
            ccb (function): Callback function to tick components
        """
        
        self.__increment_addr_reg(); self.__push_addr_bus(); self.rw.signal(True); ccb()
        self.addr_bus.signal(self._to_bits(self._to_int(self.data_bus.state) + self._to_int(self.reg_X.state), 16))

    def _calc_addr_zpy(self, ccb):
        """Steps the address registers over to the zeropage address indexed by Y

        Args:
            ccb (function): Callback function to tick components
        """
        
        self.__increment_addr_reg(); self.__push_addr_bus(); self.rw.signal(True); ccb()
        self.addr_bus.signal(self._to_bits(self._to_int(self.data_bus.state) + self._to_int(self.reg_Y.state), 16))

    def _calc_addr_ax(self, ccb):
        """Steps the address registers over to the absolute address indexed by X

        Args:
            ccb (function): Callback function to tick components
        """
        
        self.__increment_addr_reg(); self.__push_addr_bus(); self.rw.signal(True); ccb()
        addr_low = self._to_int(self.data_bus.state)
        self.__increment_addr_reg(); self.__push_addr_bus(); ccb()
        base = (self._to_int(self.data_bus.state) << 8) | addr_low
        self.addr_bus.signal(self._to_bits(base + self._to_int(self.reg_X.state), 16))

    def _calc_addr_ay(self, ccb):
        """Steps the address registers over to the absolutet address indexed by Y

        Args:
            ccb (function): Callback function to tick components
        """
        
        self.__increment_addr_reg(); self.__push_addr_bus(); self.rw.signal(True); ccb()
        addr_low = self._to_int(self.data_bus.state)
        self.__increment_addr_reg(); self.__push_addr_bus(); ccb()
        base = (self._to_int(self.data_bus.state) << 8) | addr_low
        self.addr_bus.signal(self._to_bits(base + self._to_int(self.reg_Y.state), 16))

    def _calc_addr_ix(self, ccb):
        """Steps the address registers over to the indirect address stored at zeropage+X

        Args:
            ccb (function): Callback function to tick components
        """
        
        self.__increment_addr_reg(); self.__push_addr_bus(); self.rw.signal(True); ccb()
        ptr = (self._to_int(self.data_bus.state) + self._to_int(self.reg_X.state)) & 0xFF
        self.addr_bus.signal(self._to_bits(ptr, 16)); ccb()
        addr_low = self._to_int(self.data_bus.state)
        self.addr_bus.signal(self._to_bits(ptr + 1, 16)); ccb()
        self.addr_bus.signal(self._to_bits((self._to_int(self.data_bus.state) << 8) | addr_low, 16))

    def _calc_addr_iy(self, ccb):
        """Steps the address registers over to the indirect address at zeropage indexed by Y

        Args:
            ccb (function): Callback function to tick components
        """
        
        self.__increment_addr_reg(); self.__push_addr_bus(); self.rw.signal(True); ccb()
        ptr = self._to_int(self.data_bus.state)
        self.addr_bus.signal(self._to_bits(ptr, 16)); ccb()
        addr_low = self._to_int(self.data_bus.state)
        self.addr_bus.signal(self._to_bits(ptr + 1, 16)); ccb()
        base = (self._to_int(self.data_bus.state) << 8) | addr_low
        self.addr_bus.signal(self._to_bits(base + self._to_int(self.reg_Y.state), 16))

    # ========================== OPERATION MODES ==========================

    def _read_mode(self, ccb, calc_addr, op_func, reg=None):
        """Performs the instruction in read mode

        Args:
            ccb (function): Callback function to tick components
            calc_addr (function): Addressing mode function
            op_func (function): Parent operation function
            reg (EGroup, optional): Register to perform the operation on. Defaults to None.
        """
        
        calc_addr(ccb); ccb()
        op_func(self.data_bus.state.copy(), reg.state.copy()) if reg else op_func(self.data_bus.state.copy())

    def _write_mode(self, ccb, calc_addr, reg):
        """Performs the instruction in write mode

        Args:
            ccb (function): Callback function to tick components
            calc_addr (function): Addressing mode function
            reg (EGroup): Register to pull the value from
        """
        calc_addr(ccb); self.rw.signal(False); self.data_bus.signal(reg.state.copy()); ccb(); self.rw.signal(True)

    def _rmw_mode(self, ccb, calc_addr, op_func):
        """Performs the instruction in Read-Modify-Write mode 
        (instructions that alter memory, where the data needs to be Read, then Modified and then Written back.
        For example 'DEC $2000')

        Args:
            ccb (function): Callback function to tick components
            calc_addr (function): Addressing mode function
            op_func (function): Parent operation function
        """
        
        calc_addr(ccb); ccb()
        self.data_bus.signal(op_func(self.data_bus.state.copy()))
        self.rw.signal(False); ccb(); self.rw.signal(True)

    def _branch_mode(self, ccb, condition):
        """Mode used for branching instructions

        Args:
            ccb (function): Component callback function
            condition (bool): States whether the condition is satisfied or no
        """
        self.__increment_addr_reg(); self.__push_addr_bus(); ccb()
        offset = self._to_int(self.data_bus.state)
        if offset > 127: offset -= 256
        if condition: self.__increment_addr_reg(offset)

    # ========================== META INSTRUCTIONS ==========================

    def _adc(self, val, reg_val):
        v, a = self._to_int(val), self._to_int(reg_val)
        res = a + v + (1 if self.reg_P.state[0] else 0)
        p = self.reg_P.state
        p[0] = res > 0xFF                           # carry
        p[1] = (res & 0xFF) == 0                    # zero
        p[6] = bool((a ^ res) & (v ^ res) & 0x80)   # overflow
        p[7] = bool((res & 0xFF) & 0x80)            # negative
        self.reg_P.signal(p); self.reg_ACC.signal(self._to_bits(res, 8))

    def _sbc(self, val, reg_val):
        v, a = self._to_int(val), self._to_int(reg_val)
        v = v ^ 0xFF # invert for 2's complement
        res = a + v + (1 if self.reg_P.state[0] else 0)
        p = self.reg_P.state
        p[0] = res > 0xFF                           # carry
        p[1] = (res & 0xFF) == 0                    # zero
        p[6] = bool((a ^ res) & (v ^ res) & 0x80)   # overflow
        p[7] = bool((res & 0xFF) & 0x80)            # negative
        self.reg_P.signal(p); self.reg_ACC.signal(self._to_bits(res, 8))

    def _and(self, val, reg_val): 
        res = self._to_int(reg_val) & self._to_int(val)
        p = self.reg_P.state; p[1] = (res == 0); p[7] = bool(res & 0x80); self.reg_P.signal(p)
        self.reg_ACC.signal(self._to_bits(res, 8))
        
    def _eor(self, val, reg_val): 
        res = self._to_int(reg_val) ^ self._to_int(val)
        p = self.reg_P.state; p[1] = (res == 0); p[7] = bool(res & 0x80); self.reg_P.signal(p)
        self.reg_ACC.signal(self._to_bits(res, 8))
        
    def _ora(self, val, reg_val): 
        res = self._to_int(reg_val) | self._to_int(val)
        p = self.reg_P.state; p[1] = (res == 0); p[7] = bool(res & 0x80); self.reg_P.signal(p)
        self.reg_ACC.signal(self._to_bits(res, 8))

    def _bit(self, val):
        p = self.reg_P.state; v = self._to_int(val)
        p[7] = bool(v & 0x80)                                       # negative is bit 7 of memory
        p[6] = bool(v & 0x40)                                       # overflow is bit 6 of memory
        p[1] = (v & self._to_int(self.reg_ACC.state)) == 0          # zero is ACC & memory
        self.reg_P.signal(p)
        
    def _cmp_base(self, val, reg_val):
        p = self.reg_P.state; v, r = self._to_int(val), self._to_int(reg_val)
        res = (r - v) & 0xFF
        p[0] = (r >= v)
        p[1] = (r == v)
        p[7] = bool(res & 0x80)
        self.reg_P.signal(p)

    def _lda(self, val):
        self.reg_ACC.signal(val.copy())
        p = self.reg_P.state; p[7], p[1] = val[7], (val == [False]*8); self.reg_P.signal(p)

    def _ldx(self, val): 
        self.reg_X.signal(val.copy())
        p = self.reg_P.state; p[7], p[1] = val[7], (val == [False]*8); self.reg_P.signal(p)
        
    def _ldy(self, val): 
        self.reg_Y.signal(val.copy())
        p = self.reg_P.state; p[7], p[1] = val[7], (val == [False]*8); self.reg_P.signal(p)

    def _inc(self, val):
        v = (self._to_int(val) + 1) & 0xFF
        p = self.reg_P.state; p[1], p[7] = (v == 0), bool(v & 0x80); self.reg_P.signal(p); return self._to_bits(v, 8)

    def _dec(self, val):
        v = (self._to_int(val) - 1) & 0xFF
        p = self.reg_P.state; p[1], p[7] = (v == 0), bool(v & 0x80); self.reg_P.signal(p); return self._to_bits(v, 8)

    def _asl(self, val):
        v = self._to_int(val); p = self.reg_P.state; p[0] = bool(v & 0x80)
        v = (v << 1) & 0xFF; p[1], p[7] = (v == 0), bool(v & 0x80); self.reg_P.signal(p); return self._to_bits(v, 8)

    def _lsr(self, val):
        v = self._to_int(val); p = self.reg_P.state; p[0] = bool(v & 0x01)
        v = v >> 1; p[1], p[7] = (v == 0), False; self.reg_P.signal(p); return self._to_bits(v, 8)

    def _rol(self, val):
        p = self.reg_P.state; bb = val.pop(0); val.append(p[0])
        p[0], p[1], p[7] = bb, (val == [False]*8), val[7]; self.reg_P.signal(p); return val

    def _ror(self, val):
        p = self.reg_P.state; bb = val.pop(); val.insert(0, p[0])
        p[0], p[1], p[7] = bb, (val == [False]*8), val[7]; self.reg_P.signal(p); return val

    # ========================== INSTRUCTION MAPS ==========================
    def _adc_i(self, ccb): self._read_mode(ccb, self._calc_addr_imm, self._adc, self.reg_ACC)
    def _adc_zp(self, ccb): self._read_mode(ccb, self._calc_addr_zp, self._adc, self.reg_ACC)
    def _adc_a(self, ccb): self._read_mode(ccb, self._calc_addr_abs, self._adc, self.reg_ACC)
    def _adc_ix(self, ccb): self._read_mode(ccb, self._calc_addr_ix, self._adc, self.reg_ACC)
    def _adc_iy(self, ccb): self._read_mode(ccb, self._calc_addr_iy, self._adc, self.reg_ACC)
    def _adc_zpx(self, ccb): self._read_mode(ccb, self._calc_addr_zpx, self._adc, self.reg_ACC)
    def _adc_ax(self, ccb): self._read_mode(ccb, self._calc_addr_ax, self._adc, self.reg_ACC)
    def _adc_ay(self, ccb): self._read_mode(ccb, self._calc_addr_ay, self._adc, self.reg_ACC)

    def _and_i(self, ccb): self._read_mode(ccb, self._calc_addr_imm, self._and, self.reg_ACC)
    def _and_zp(self, ccb): self._read_mode(ccb, self._calc_addr_zp, self._and, self.reg_ACC)
    def _and_a(self, ccb): self._read_mode(ccb, self._calc_addr_abs, self._and, self.reg_ACC)
    def _and_ix(self, ccb): self._read_mode(ccb, self._calc_addr_ix, self._and, self.reg_ACC)
    def _and_iy(self, ccb): self._read_mode(ccb, self._calc_addr_iy, self._and, self.reg_ACC)
    def _and_zpx(self, ccb): self._read_mode(ccb, self._calc_addr_zpx, self._and, self.reg_ACC)
    def _and_ax(self, ccb): self._read_mode(ccb, self._calc_addr_ax, self._and, self.reg_ACC)
    def _and_ay(self, ccb): self._read_mode(ccb, self._calc_addr_ay, self._and, self.reg_ACC)

    def _cmp_i(self, ccb): self._read_mode(ccb, self._calc_addr_imm, self._cmp_base, self.reg_ACC)
    def _cmp_zp(self, ccb): self._read_mode(ccb, self._calc_addr_zp, self._cmp_base, self.reg_ACC)
    def _cmp_a(self, ccb): self._read_mode(ccb, self._calc_addr_abs, self._cmp_base, self.reg_ACC)
    def _cmp_ix(self, ccb): self._read_mode(ccb, self._calc_addr_ix, self._cmp_base, self.reg_ACC)
    def _cmp_iy(self, ccb): self._read_mode(ccb, self._calc_addr_iy, self._cmp_base, self.reg_ACC)
    def _cmp_zpx(self, ccb): self._read_mode(ccb, self._calc_addr_zpx, self._cmp_base, self.reg_ACC)
    def _cmp_ax(self, ccb): self._read_mode(ccb, self._calc_addr_ax, self._cmp_base, self.reg_ACC)
    def _cmp_ay(self, ccb): self._read_mode(ccb, self._calc_addr_ay, self._cmp_base, self.reg_ACC)

    def _eor_i(self, ccb): self._read_mode(ccb, self._calc_addr_imm, self._eor, self.reg_ACC)
    def _eor_zp(self, ccb): self._read_mode(ccb, self._calc_addr_zp, self._eor, self.reg_ACC)
    def _eor_a(self, ccb): self._read_mode(ccb, self._calc_addr_abs, self._eor, self.reg_ACC)
    def _eor_ix(self, ccb): self._read_mode(ccb, self._calc_addr_ix, self._eor, self.reg_ACC)
    def _eor_iy(self, ccb): self._read_mode(ccb, self._calc_addr_iy, self._eor, self.reg_ACC)
    def _eor_zpx(self, ccb): self._read_mode(ccb, self._calc_addr_zpx, self._eor, self.reg_ACC)
    def _eor_ax(self, ccb): self._read_mode(ccb, self._calc_addr_ax, self._eor, self.reg_ACC)
    def _eor_ay(self, ccb): self._read_mode(ccb, self._calc_addr_ay, self._eor, self.reg_ACC)

    def _lda_i(self, ccb): self._read_mode(ccb, self._calc_addr_imm, self._lda)
    def _lda_zp(self, ccb): self._read_mode(ccb, self._calc_addr_zp, self._lda)
    def _lda_a(self, ccb): self._read_mode(ccb, self._calc_addr_abs, self._lda)
    def _lda_ix(self, ccb): self._read_mode(ccb, self._calc_addr_ix, self._lda)
    def _lda_iy(self, ccb): self._read_mode(ccb, self._calc_addr_iy, self._lda)
    def _lda_zpx(self, ccb): self._read_mode(ccb, self._calc_addr_zpx, self._lda)
    def _lda_ax(self, ccb): self._read_mode(ccb, self._calc_addr_ax, self._lda)
    def _lda_ay(self, ccb): self._read_mode(ccb, self._calc_addr_ay, self._lda)

    def _ora_i(self, ccb): self._read_mode(ccb, self._calc_addr_imm, self._ora, self.reg_ACC)
    def _ora_zp(self, ccb): self._read_mode(ccb, self._calc_addr_zp, self._ora, self.reg_ACC)
    def _ora_a(self, ccb): self._read_mode(ccb, self._calc_addr_abs, self._ora, self.reg_ACC)
    def _ora_ix(self, ccb): self._read_mode(ccb, self._calc_addr_ix, self._ora, self.reg_ACC)
    def _ora_iy(self, ccb): self._read_mode(ccb, self._calc_addr_iy, self._ora, self.reg_ACC)
    def _ora_zpx(self, ccb): self._read_mode(ccb, self._calc_addr_zpx, self._ora, self.reg_ACC)
    def _ora_ax(self, ccb): self._read_mode(ccb, self._calc_addr_ax, self._ora, self.reg_ACC)
    def _ora_ay(self, ccb): self._read_mode(ccb, self._calc_addr_ay, self._ora, self.reg_ACC)

    def _sbc_i(self, ccb): self._read_mode(ccb, self._calc_addr_imm, self._sbc, self.reg_ACC)
    def _sbc_zp(self, ccb): self._read_mode(ccb, self._calc_addr_zp, self._sbc, self.reg_ACC)
    def _sbc_a(self, ccb): self._read_mode(ccb, self._calc_addr_abs, self._sbc, self.reg_ACC)
    def _sbc_ix(self, ccb): self._read_mode(ccb, self._calc_addr_ix, self._sbc, self.reg_ACC)
    def _sbc_iy(self, ccb): self._read_mode(ccb, self._calc_addr_iy, self._sbc, self.reg_ACC)
    def _sbc_zpx(self, ccb): self._read_mode(ccb, self._calc_addr_zpx, self._sbc, self.reg_ACC)
    def _sbc_ax(self, ccb): self._read_mode(ccb, self._calc_addr_ax, self._sbc, self.reg_ACC)
    def _sbc_ay(self, ccb): self._read_mode(ccb, self._calc_addr_ay, self._sbc, self.reg_ACC)

    def _sta_zp(self, ccb): self._write_mode(ccb, self._calc_addr_zp, self.reg_ACC)
    def _sta_a(self, ccb): self._write_mode(ccb, self._calc_addr_abs, self.reg_ACC)
    def _sta_ix(self, ccb): self._write_mode(ccb, self._calc_addr_ix, self.reg_ACC)
    def _sta_iy(self, ccb): self._write_mode(ccb, self._calc_addr_iy, self.reg_ACC)
    def _sta_zpx(self, ccb): self._write_mode(ccb, self._calc_addr_zpx, self.reg_ACC)
    def _sta_ax(self, ccb): self._write_mode(ccb, self._calc_addr_ax, self.reg_ACC)
    def _sta_ay(self, ccb): self._write_mode(ccb, self._calc_addr_ay, self.reg_ACC)

    def _cpx_i(self, ccb): self._read_mode(ccb, self._calc_addr_imm, self._cmp_base, self.reg_X)
    def _cpx_a(self, ccb): self._read_mode(ccb, self._calc_addr_abs, self._cmp_base, self.reg_X)
    def _cpx_zp(self, ccb): self._read_mode(ccb, self._calc_addr_zp, self._cmp_base, self.reg_X)

    def _cpy_i(self, ccb): self._read_mode(ccb, self._calc_addr_imm, self._cmp_base, self.reg_Y)
    def _cpy_a(self, ccb): self._read_mode(ccb, self._calc_addr_abs, self._cmp_base, self.reg_Y)
    def _cpy_zp(self, ccb): self._read_mode(ccb, self._calc_addr_zp, self._cmp_base, self.reg_Y)

    def _ldx_i(self, ccb): self._read_mode(ccb, self._calc_addr_imm, self._ldx)
    def _ldx_a(self, ccb): self._read_mode(ccb, self._calc_addr_abs, self._ldx)
    def _ldx_zp(self, ccb): self._read_mode(ccb, self._calc_addr_zp, self._ldx)
    def _ldx_ay(self, ccb): self._read_mode(ccb, self._calc_addr_ay, self._ldx)
    def _ldx_zpy(self, ccb): self._read_mode(ccb, self._calc_addr_zpy, self._ldx)

    def _ldy_i(self, ccb): self._read_mode(ccb, self._calc_addr_imm, self._ldy)
    def _ldy_a(self, ccb): self._read_mode(ccb, self._calc_addr_abs, self._ldy)
    def _ldy_zp(self, ccb): self._read_mode(ccb, self._calc_addr_zp, self._ldy)
    def _ldy_ax(self, ccb): self._read_mode(ccb, self._calc_addr_ax, self._ldy)
    def _ldy_zpx(self, ccb): self._read_mode(ccb, self._calc_addr_zpx, self._ldy)

    def _stx_a(self, ccb): self._write_mode(ccb, self._calc_addr_abs, self.reg_X)
    def _stx_zp(self, ccb): self._write_mode(ccb, self._calc_addr_zp, self.reg_X)
    def _stx_zpy(self, ccb): self._write_mode(ccb, self._calc_addr_zpy, self.reg_X)

    def _sty_a(self, ccb): self._write_mode(ccb, self._calc_addr_abs, self.reg_Y)
    def _sty_zp(self, ccb): self._write_mode(ccb, self._calc_addr_zp, self.reg_Y)
    def _sty_zpx(self, ccb): self._write_mode(ccb, self._calc_addr_zpx, self.reg_Y)

    def _asl_a(self, ccb): self._rmw_mode(ccb, self._calc_addr_abs, self._asl)
    def _asl_zp(self, ccb): self._rmw_mode(ccb, self._calc_addr_zp, self._asl)
    def _asl_zpx(self, ccb): self._rmw_mode(ccb, self._calc_addr_zpx, self._asl)
    def _asl_ax(self, ccb): self._rmw_mode(ccb, self._calc_addr_ax, self._asl)
    def _asl_acc(self, ccb): self.reg_ACC.signal(self._asl(self.reg_ACC.state.copy()))

    def _lsr_a(self, ccb): self._rmw_mode(ccb, self._calc_addr_abs, self._lsr)
    def _lsr_zp(self, ccb): self._rmw_mode(ccb, self._calc_addr_zp, self._lsr)
    def _lsr_zpx(self, ccb): self._rmw_mode(ccb, self._calc_addr_zpx, self._lsr)
    def _lsr_ax(self, ccb): self._rmw_mode(ccb, self._calc_addr_ax, self._lsr)
    def _lsr_acc(self, ccb): self.reg_ACC.signal(self._lsr(self.reg_ACC.state.copy()))

    def _rol_a(self, ccb): self._rmw_mode(ccb, self._calc_addr_abs, self._rol)
    def _rol_zp(self, ccb): self._rmw_mode(ccb, self._calc_addr_zp, self._rol)
    def _rol_zpx(self, ccb): self._rmw_mode(ccb, self._calc_addr_zpx, self._rol)
    def _rol_ax(self, ccb): self._rmw_mode(ccb, self._calc_addr_ax, self._rol)
    def _rol_acc(self, ccb): self.reg_ACC.signal(self._rol(self.reg_ACC.state.copy()))

    def _ror_a(self, ccb): self._rmw_mode(ccb, self._calc_addr_abs, self._ror)
    def _ror_zp(self, ccb): self._rmw_mode(ccb, self._calc_addr_zp, self._ror)
    def _ror_zpx(self, ccb): self._rmw_mode(ccb, self._calc_addr_zpx, self._ror)
    def _ror_ax(self, ccb): self._rmw_mode(ccb, self._calc_addr_ax, self._ror)
    def _ror_acc(self, ccb): self.reg_ACC.signal(self._ror(self.reg_ACC.state.copy()))

    def _inc_a(self, ccb): self._rmw_mode(ccb, self._calc_addr_abs, self._inc)
    def _inc_zp(self, ccb): self._rmw_mode(ccb, self._calc_addr_zp, self._inc)
    def _inc_zpx(self, ccb): self._rmw_mode(ccb, self._calc_addr_zpx, self._inc)
    def _inc_ax(self, ccb): self._rmw_mode(ccb, self._calc_addr_ax, self._inc)

    def _dec_a(self, ccb): self._rmw_mode(ccb, self._calc_addr_abs, self._dec)
    def _dec_zp(self, ccb): self._rmw_mode(ccb, self._calc_addr_zp, self._dec)
    def _dec_zpx(self, ccb): self._rmw_mode(ccb, self._calc_addr_zpx, self._dec)
    def _dec_ax(self, ccb): self._rmw_mode(ccb, self._calc_addr_ax, self._dec)

    def _bit_a(self, ccb): self._read_mode(ccb, self._calc_addr_abs, self._bit)
    def _bit_zp(self, ccb): self._read_mode(ccb, self._calc_addr_zp, self._bit)

    def _inx(self, ccb): self.reg_X.signal(self._inc(self.reg_X.state.copy()))
    def _iny(self, ccb): self.reg_Y.signal(self._inc(self.reg_Y.state.copy()))
    def _dex(self, ccb): self.reg_X.signal(self._dec(self.reg_X.state.copy()))
    def _dey(self, ccb): self.reg_Y.signal(self._dec(self.reg_Y.state.copy()))

    def _tax(self, ccb): self.reg_X.signal(self.reg_ACC.state.copy())
    def _tay(self, ccb): self.reg_Y.signal(self.reg_ACC.state.copy())
    def _txa(self, ccb): self.reg_ACC.signal(self.reg_X.state.copy())
    def _tya(self, ccb): self.reg_ACC.signal(self.reg_Y.state.copy())
    def _tsx(self, ccb): self.reg_X.signal(self.reg_S.state.copy())
    def _txs(self, ccb): self.reg_S.signal(self.reg_X.state.copy())

    def _pha(self, ccb): self._push_stack(ccb, self.reg_ACC.state.copy())
    def _php(self, ccb): self._push_stack(ccb, self.reg_P.state.copy())
    def _pla(self, ccb): self.reg_ACC.signal(self._pop_stack(ccb))
    def _plp(self, ccb): self.reg_P.signal(self._pop_stack(ccb))

    def _bcc(self, ccb): self._branch_mode(ccb, not self.reg_P.state[0])
    def _bcs(self, ccb): self._branch_mode(ccb, self.reg_P.state[0])
    def _beq(self, ccb): self._branch_mode(ccb, self.reg_P.state[1])
    def _bmi(self, ccb): self._branch_mode(ccb, self.reg_P.state[7])
    def _bne(self, ccb): self._branch_mode(ccb, not self.reg_P.state[1])
    def _bpl(self, ccb): self._branch_mode(ccb, not self.reg_P.state[7])
    def _bvc(self, ccb): self._branch_mode(ccb, not self.reg_P.state[6])
    def _bvs(self, ccb): self._branch_mode(ccb, self.reg_P.state[6])

    def _clc(self, ccb): p = self.reg_P.state; p[0] = False; self.reg_P.signal(p)
    def _cld(self, ccb): p = self.reg_P.state; p[3] = False; self.reg_P.signal(p)
    def _cli(self, ccb): p = self.reg_P.state; p[2] = False; self.reg_P.signal(p)
    def _clv(self, ccb): p = self.reg_P.state; p[6] = False; self.reg_P.signal(p)
    def _sec(self, ccb): p = self.reg_P.state; p[0] = True; self.reg_P.signal(p)
    def _sed(self, ccb): p = self.reg_P.state; p[3] = True; self.reg_P.signal(p)
    def _sei(self, ccb): p = self.reg_P.state; p[2] = True; self.reg_P.signal(p)

    def _nop(self, ccb): pass
    def _brk(self, ccb): self.run = False
    def _brpnt(self, ccb): self._breaking = not self._breaking
    def _rti(self, ccb): raise NotImplementedError("RTI not implemented yet")

    def _jmp_a(self, ccb):
        self.__increment_addr_reg(); self.__push_addr_bus(); ccb()
        first = self.data_bus.state.copy()
        self.__increment_addr_reg(); self.__push_addr_bus(); ccb()
        new_pc = self._to_bits(self._to_int(self.data_bus.state + first) - 1, 16)
        self.reg_PCH.signal(new_pc[0:8])
        self.reg_PCL.signal(new_pc[8:16])

    def _jmp_ind(self, ccb):
        self.__increment_addr_reg(); self.__push_addr_bus(); ccb()
        first = self.data_bus.state.copy()
        self.__increment_addr_reg(); self.__push_addr_bus(); ccb()
        second = self.data_bus.state.copy()
        self.addr_bus.signal(second + first); ccb()
        first = self.data_bus.state.copy()
        self.__increment_addr_reg(); self.__push_addr_bus(); ccb()
        self.reg_PCL.signal(first)
        self.reg_PCH.signal(self.data_bus.state.copy())

    def _jsr_a(self, ccb):
        self.__increment_addr_reg(); self.__push_addr_bus(); ccb()
        addr_low = self.data_bus.state.copy()
        self.__increment_addr_reg(); self.__push_addr_bus(); ccb()
        addr_high = self.data_bus.state.copy()
        
        self._push_stack(ccb, self.reg_PCH.state.copy())
        self._push_stack(ccb, self.reg_PCL.state.copy())
        
        self.reg_PCL.signal(addr_low)
        self.reg_PCH.signal(addr_high)
        self.__increment_addr_reg(-1)

    def _rts(self, ccb): 
        self.__increment_addr_reg(); self.__push_addr_bus(); ccb()
        addr_low = self._pop_stack(ccb)
        addr_high = self._pop_stack(ccb)
        self.reg_PCL.signal(addr_low)
        self.reg_PCH.signal(addr_high)

    # ========================== MAIN LOOP ==========================

    def update(self, ccb):
        self.__cycles += 1
        self.cout1.signal(not self.cout1.state)
        self.cout2.signal(not self.cout1.state)
        
        print("="*20 + f"CYCLE: {self.__cycles}" + "="*20)
        self.rw.signal(True)
        self.__push_addr_bus()
        ccb()
        
        inst = int(''.join(['1' if x else '0' for x in self.data_bus.state]), 2)
        #m = self.get_debug()
        #
        #print('\n'.join(("SY6502-INST :", 
        #                 f"DBS :{m['db']:#010b} ({hex(m['db'])})", 
        #                 f"PCL :{m['pcl']:#010b} ({hex(m['pcl'])})", 
        #                 f"PCH :{m['pch']:#010b} ({hex(m['pch'])})", 
        #                 f"ACC :{m['acc']:#010b} ({hex(m['acc'])})", 
        #                 f"X   :{m['x']:#010b} ({hex(m['x'])})", 
        #                 f"Y   :{m['y']:#010b} ({hex(m['y'])})", 
        #                 f"P   :{m['p']:#010b} ({hex(m['p'])})", 
        #                 f"S   :{m['s']:#010b} ({hex(m['s'])})", 
        #                 f"RW  :{m['rw']}")))
        
        if inst in self.instruction_set:
            self.instruction_set[inst](ccb)
        
        #m = self.get_debug()
        #print('\n'.join(("SY6502-EXEC :", 
        #                 f"DBS :{m['db']:#010b} ({hex(m['db'])})", 
        #                 f"PCL :{m['pcl']:#010b} ({hex(m['pcl'])})", 
        #                 f"PCH :{m['pch']:#010b} ({hex(m['pch'])})", 
        #                 f"ACC :{m['acc']:#010b} ({hex(m['acc'])})", 
        #                 f"X   :{m['x']:#010b} ({hex(m['x'])})", 
        #                 f"Y   :{m['y']:#010b} ({hex(m['y'])})", 
        #                 f"P   :{m['p']:#010b} ({hex(m['p'])})", 
        #                 f"S   :{m['s']:#010b} ({hex(m['s'])})", 
        #                 f"RW  :{m['rw']}")))
        
        self.__increment_addr_reg()


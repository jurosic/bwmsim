.extern DIV_16U

.equ __arg_print_uint16_ptr,   0xFE
.equ __print_uint16_high,      $0x7FF8
.equ __print_uint16_low,       $0x7FF9
.equ __print_uint16_base_high, $0x7FF6
.equ __print_uint16_base_low,  $0x7FF7

.equ __print_listener_buffer,  $0x2020
.equ __print_listener_flags,   $0x2021

PRINT_UINT16:
	; prints the unsigned 16bit integer
	; provided by a ptr on zp

	; uses registers X and Y for internal logic
	; but restores them

	; back up registers
	TXA
	PHA
	TYA
	PHA

	; back up integer
	LDY #0
	LDA (__arg_print_uint16_ptr),Y
	STA __print_uint16_high

	INY

	LDA (__arg_print_uint16_ptr),Y
	STA __print_uint16_low

	_PRINT_UINT16_LOOP:
		LDA #0
		STA __print_uint16_base_high
		LDA #10
		STA __print_uint16_base_low
		
		; set pointers
		; common prefixes
		LDA #0x7F
		STA 0xFD
		STA 0xFF

		; dividend
		LDA #0xF8
		STA 0xFC

		; divisor
		LDA #0xF6
		STA 0xFE

		; divide
		JSR DIV_16U

		; after division, our numbers 
		; are overwritten, but fret not
		; we only print the remainder
		; and redivide the quotient
		LDA __print_uint16_base_low
		STA __print_listener_buffer
		; since the remainder will always
		; be in the range 0-9, we can use
		; the lower byte only and call 
		; set flags to char + reverse

		LDA #0b00000101
		STA __print_listener_flags

		; check if quotient is 0
		LDA __print_uint16_high
		CMP #0

		BNE _PRINT_UINT16_LOOP

		LDA __print_uint16_low
		CMP #0

		BNE _PRINT_UINT16_LOOP

	; cleanup

	; restore regs
	PLA
	TAY
	PLA
	TAX

	RTS

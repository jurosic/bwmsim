.extern DIV_16U

.equ __arg_print_uint16_ptr,   0xFE

;.equ __print_uint16_high,      $0x7FF8
;.equ __print_uint16_low,       $0x7FF9
;.equ __print_uint16_base_high, $0x7FF6
;.equ __print_uint16_base_low,  $0x7FF7

.res __print_uint16, 2
.res __print_uint16_base, 2

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
	STA __print_uint16

	INY

	LDA (__arg_print_uint16_ptr),Y
	STA __print_uint16+1

	_PRINT_UINT16_LOOP:
		LDA #10
		STA __print_uint16_base
		LDA #0
		STA __print_uint16_base+1
		
		; set pointers
		; dividend
		LDA >__print_uint16
		STA 0xFC
		; divisor
		LDA >__print_uint16_base
		STA 0xFE

		; common
		LDA <__print_uint16
		STA 0xFD
		STA 0xFF

		; divide
		JSR DIV_16U

		; after division, our numbers 
		; are overwritten, but fret not
		; we only print the remainder
		; and redivide the quotient
		LDA __print_uint16_base
		STA __print_listener_buffer
		; since the remainder will always
		; be in the range 0-9, we can use
		; the lower byte only and call 
		; set flags to char + reverse

		LDA #0b00000101
		STA __print_listener_flags

		; check if quotient is 0
		LDA __print_uint16
		CMP #0

		BNE _PRINT_UINT16_LOOP

		LDA __print_uint16+1
		CMP #0

		BNE _PRINT_UINT16_LOOP

	;send reverse
	LDA #0b01000000
	STA __print_listener_flags

	;send newline
	LDA #0b00100000
	STA __print_listener_flags

	;send EOF
	LDA #0b10000000
	STA __print_listener_flags

	; cleanup

	; restore regs
	PLA
	TAY
	PLA
	TAX

	RTS

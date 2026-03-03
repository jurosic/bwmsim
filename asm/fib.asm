.org $8000
.extern ADD_16

; ZP:
; 00 01 - fibm
; 02 03 - fib1
; 04 05 - fib2
; 06    - cnter

; i should really add .data support :(


;test out warning for same value constants
.equ this_should_warn, $0x2003
;this should ignore
.ignore
.equ this_should_ignore, $0x2001
START:
	;testing add_16
	CLC
	CLV
	CLD

	LDA #0x01
	STA 0x01
	STA 0x03
	LDA #0x00 ; reset ram, just to be sure
	STA 0x00
	STA 0x02
	STA 0x04
	STA 0x05
	STA 0x06


FIB:
	;fib2 <- fibm
	LDA 0x00
	STA 0x04
	LDA 0x01
	STA 0x05
	
	;fibm + fib1
	LDA 0x00
	STA __adder_t_high
	LDA 0x01 
	STA __adder_t_low

	LDA 0x02
	STA __adder_m_high
	LDA 0x03
	STA __adder_m_low

	JSR ADD_16

	LDA __adder_t_low
	STA 0x01
	LDA __adder_t_high
	STA 0x00

	JSR SEND_FIB_16

	;fib1 <- fib2
	LDA 0x05
	STA 0x03
	LDA 0x04
	STA 0x02
	
	INC 0x06
	LDA 0x06
	CMP #0x16

	BNE FIB

FIN:
	JSR SEND_FIN
	LDA #0xFF
	BRK

SEND_FIB_16:
	.equ _int_nl_flag, #0b10000001
	;sends 16 bits to reserved mem
	;to be read externaly
	; $2010 - Low
	; $2011 - High
	; $2012 - Flags (
	;		all zeroes - external source read, waiting
	;       LSB   1 - INT
	;		LSB < 1 - CHAR (only uses LOW)
	;	)
	LDA 0x00
	STA $0x2011
	LDA 0x01
	STA $0x2010

	LDA _int_nl_flag
	STA $0x2012

	RTS

SEND_FIN:
	.equ _char_flag, #0b00000010
	.equ _char_nl_flag, #0b10000010

	LDA #0x46
	STA $0x2010
	LDA _char_flag
	STA $0x2012

	LDA #0x49
	STA $0x2010
	LDA _char_flag
	STA $0x2012

	LDA #0x4E
	STA $0x2010
	LDA _char_nl_flag 
	STA $0x2012

	RTS

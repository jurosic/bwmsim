.org $8000
.extern ADD_16

; ZP:
; 00 01 - fibm
; 02 03 - fib1
; 04 05 - fib2
; 06    - cnter

; i should really add .text support :(
START:
	;testing add_16
	CLC
	CLV
	CLD

	LDA #01
	STA 01
	STA 03
	LDA #00 ; reset ram, just to be sure
	STA 00
	STA 02
	STA 04
	STA 05
	STA 06


FIB:
	;fib2 <- fibm
	LDA 00
	STA 04
	LDA 01
	STA 05
	
	;fibm + fib1
	LDA 00
	STA $2003
	LDA 01 
	STA $2002

	LDA 02
	STA $2001
	LDA 03
	STA $2000

	JSR ADD_16

	LDA $2002
	STA 01
	LDA $2003
	STA 00

	JSR SEND_FIB_16

	;fib1 <- fib2
	LDA 05
	STA 03
	LDA 04
	STA 02
	
	INC 06
	LDA 06
	CMP #16

	BNE FIB

FIN:
	JSR SEND_FIN
	LDA #FF
	BRK

SEND_FIB_16:
	;sends 16 bits to reserved mem
	;to be read externaly
	; $2010 - Low
	; $2011 - High
	; $2012 - Flags (
	;		all zeroes - external source read, waiting
	;       LSB   1 - INT
	;		LSB < 1 - CHAR (only uses LOW)
	;	)
	LDA 00
	STA $2011
	LDA 01
	STA $2010

	LDA #81
	STA $2012

	RTS

SEND_FIN:
	LDA #46
	STA $2010
	LDA #02
	STA $2012

	LDA #49
	STA $2010
	LDA #02
	STA $2012

	LDA #4E
	STA $2010
	LDA #82
	STA $2012

	RTS

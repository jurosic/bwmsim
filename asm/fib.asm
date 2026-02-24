.org $8000

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
	
	;fib1 <- fib2
	LDA 05
	STA 03
	LDA 04
	STA 02
	
	INC 06
	LDA 06
	CMP #15

	BNE FIB

FIN:
	LDA #FF
	BRK

ADD_16:
	; $2000 - M lower
	; $2001 - M Higher
	; $2002 - T Lower
	; $2003 - T Higher
	CLC
	CLD
	CLV

	;add lower halves together
	LDA $2002
	ADC $2000
	STA $2002

	;add higher halves together
	LDA $2003
	ADC $2001
	STA $2003

	CLC ; cleanup

	RTS

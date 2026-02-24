.org $8000

; ZP:
; 00 - fibm
; 01 - fib1
; 02 - fib2
START:
	CLC
	CLV
	CLD

	LDA #01
	STA 00
	STA 01
	LDA #00
	STA 02

FIB:
	;fib2 <- fibm
	LDA 00
	STA 02
	
	;fibm + fib1
	LDA 00
	ADC 01
	BCS FIN
	STA 00
	PHA
	
	;fib1 <- fib2
	LDA 02
	STA 01
	
	BCC FIB

FIN:
	LDA #FF
	BRK

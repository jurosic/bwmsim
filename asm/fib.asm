.org $8000

; ZP:
; 00 - fibm
; 01 - fib1
; 02 - fib2
START:
	;testing add_16

	;push 500 on stack
	LDA #F4
	PHA
	LDA #01
	PHA

	;push 500 on stack
	LDA #F4
	PHA
	LDA #01
	PHA

	;try adding
	JSR ADD_16
	;after we return we NEED to update SP to account for 
	;arguments.
	TSX;
	TXA;
	ADC #03
	TAX;
	TXS;

	; if we returned we store FA in acc
	LDA #FA

	;break
	BRK

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
	ADC 01
	BCS FIN
	STA 00
	PHA
	
	;fib1 <- fib2
	LDA 02
	STA 01
	
	JMP FIB

FIN:
	LDA #FF
	BRK

;accepts four args on stack, TLA, THA, MLA, MHA 
ADD_16:
	;save to temporary addresses

	;okay this expects four args, lets think here.
	; STACK STATUS:
	;	RAH
	;   RAL - this and ^ byte together resolve to ret addtess
	;	MHA
	;	MLA - this and ^ byte together resolve to manipulator 16bit int
	;	THA
	;	TLA - this and ^ byte together resolve to target 16 bit int


	;we know we expect 4 args so first lets skip 2 values (ret add)
	PLA
	PLA

	;now sp is at values, we load them

	CLC
	CLD
	CLV

	;MHA, MLA
	PLA 
	STA $2001
	PLA 
	STA $2000

	;THA, TLA
	PLA
	STA $2003
	PLA
	STA $2002

	!

	;add lower halves together
	LDA $2002
	ADC $2000
	STA $2002

	LDA $2003 ;ldaing here for efficiency
	;branch on carry and add 1?
	BCC _NO_CARRY

	ADC #01
	
	_NO_CARRY:
	;add higher halves together
	;THA already loaded
	ADC $2001

	!

	;after execution ends we need to bump up the stack pointer by 6;
	TSX ;transfer stack to x
	TXA ; transfer x to acc
	CLC
	ADC #FA; add -7 
	TAX;
	TXS;

	;maybe js maybe this might work..
	;this WILL memory leak if u dont know how this SR works:sob:

	RTS

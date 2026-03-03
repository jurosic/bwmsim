.equ __p_flags,       $0x2020
.equ __p_buffer,      $0x2021
.equ __p_arrptr_low,  0xFF
.equ __p_arrptr_high, 0xFE
.equ __p_arrlen,      0xFD

PRINT:
	; 'prints' 8-bit array supplied on stack 
	; uses X register for counter
	; expects arguments like so:
	; 	0 - rethigh
	;	1 - retlow
	;	2 - arraylow
	;	3 - arrayhigh
	;   4 - arraylen

	CLC
	CLD
	CLV

	;load arrlen
	PLA 
	STA __p_arrlen

	;load arrayhigh
	PLA
	STA __p_arrptr_high

	;load arraylow
	PLA 
	STA __p_arrptr_low

	LDY #0

	__PRINT_LOOP:
		;load next char
		LDA (__p_arrptr_high),Y

		STA __p_buffer

		LDA #0xFF
		STA __p_flags

		INY

		CPY __p_arrlen

		BNE __PRINT_LOOP

	; perform some arithmetic on the pointers to return
	; reuse old memory

	PLA 
	ADC #12
	STA __p_arrlen
	PLA 
	ADC #0
	PHA
	LDA __p_arrlen
	PHA

	CLC
	CLV

	RTS
	;43



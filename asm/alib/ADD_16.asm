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


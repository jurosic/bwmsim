.equ __adder_m_low,  $0x2000
.equ __adder_m_high, $0x2001
.equ __adder_t_low,  $0x2002
.equ __adder_t_high, $0x2003

ADD_16:
	; $2000 - M lower
	; $2001 - M Higher
	; $2002 - T Lower
	; $2003 - T Higher
	CLC
	CLD
	CLV

	;add lower halves together
	LDA __adder_t_low
	ADC __adder_m_low
	STA __adder_t_low

	;add higher halves together
	LDA __adder_t_high
	ADC __adder_m_high
	STA __adder_t_high

	CLC ; cleanup

	RTS


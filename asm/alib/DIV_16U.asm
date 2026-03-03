; argument pointers
.equ __arg_div_16u_divisor_ptr,  0xFE
.equ __arg_div_16u_dividend_ptr, 0xFC

; 
.equ __div_16u_divisor_buffer_high,  $0x7FFE
.equ __div_16u_divisor_buffer_low,   $0x7FFF ; i should add support
.equ __div_16u_dividend_buffer_high, $0x7FFC ; for arg arithmetic 
.equ __div_16u_dividend_buffer_low,  $0x7FFD
.equ __div_16u_quotient_high,        $0x7FFA
.equ __div_16u_quotient_low,         $0x7FFB

DIV_16U:
	; performs unsigned division
	; on the integers provided by zp
	; pointers

	; uses registers X and Y for internal logic,
	; but restores them
	
	; provides output by overwriting 
	; zpptr divident high to quotient
	; zpptr divisor high to remainder
	
	; this sr only counts to 

	; store X and Y
	TXA
	PHA
	TYA
	PHA


	; copy values into buffer
	LDY #0
	LDA (__arg_div_16u_dividend_ptr),Y
	STA __div_16u_dividend_buffer_high
	LDA (__arg_div_16u_divisor_ptr),Y
	STA __div_16u_divisor_buffer_high

	INY

	LDA (__arg_div_16u_dividend_ptr),Y
	STA __div_16u_dividend_buffer_low
	LDA (__arg_div_16u_divisor_ptr),Y
	STA __div_16u_divisor_buffer_low

	CLD
	LDA #0
	STA __div_16u_quotient_high
	STA __div_16u_quotient_low

	_DIV_16U_LOOP:
		; compare if dividend is smaller than divisor
		; checks high bytes
		LDA __div_16u_dividend_buffer_low
		CMP __div_16u_divisor_buffer_low
		
		LDA __div_16u_dividend_buffer_high
		SBC __div_16u_divisor_buffer_high
	
		; same stuff
		BCC _DIV_16U_END
		
		;------------------------------

		SEC ;just in case

		; subtract divisor from divident
		LDA __div_16u_dividend_buffer_low
		SBC __div_16u_divisor_buffer_low
		STA __div_16u_dividend_buffer_low

		LDA __div_16u_dividend_buffer_high
		SBC __div_16u_divisor_buffer_high
		STA __div_16u_dividend_buffer_high

		CLC
		LDA __div_16u_quotient_low
		ADC #0x1
		STA __div_16u_quotient_low

		LDA __div_16u_quotient_high
		ADC #0x0
		STA __div_16u_quotient_high

		JMP _DIV_16U_LOOP

	_DIV_16U_END:
		; store results and 
		; restore registers

		LDY #0

		LDA __div_16u_dividend_buffer_high
		STA (__arg_div_16u_divisor_ptr),Y
		LDA __div_16u_quotient_high
		STA (__arg_div_16u_dividend_ptr),Y

		INY

		LDA __div_16u_dividend_buffer_low
		STA (__arg_div_16u_divisor_ptr),Y
		LDA __div_16u_quotient_low
		STA (__arg_div_16u_dividend_ptr),Y

		PLA
		TAY
		PLA
		TAX

		RTS


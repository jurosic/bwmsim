; argument pointers
.equ __arg_div_16u_divisor_ptr,  0xFE
.equ __arg_div_16u_dividend_ptr, 0xFC

; 
;.equ __div_16u_divisor_buffer_high,  $0x7FFE
;.equ __div_16u_divisor_buffer_low,   $0x7FFF ; i should add support
;.equ __div_16u_dividend_buffer_high, $0x7FFC ; for arg arithmetic 
;.equ __div_16u_dividend_buffer_low,  $0x7FFD
;.equ __div_16u_quotient_high,        $0x7FFA
;.equ __div_16u_quotient_low,         $0x7FFB

.res __div_16u_divisor_buffer, 2
.res __div_16u_dividend_buffer, 2
.res __div_16u_quotient, 2

DIV_16U:
	; performs unsigned division
	; on the integers provided by zp
	; pointers

	; uses registers X and Y for internal logic,
	; but restores them
	
	; provides output by overwriting 
	; zpptr divident to quotient
	; zpptr divisor to remainder
	
	; this sr only counts to 

	; store X and Y
	TXA
	PHA
	TYA
	PHA


	; copy values into buffer
	LDY #0
	LDA (__arg_div_16u_dividend_ptr),Y
	STA __div_16u_dividend_buffer
	LDA (__arg_div_16u_divisor_ptr),Y
	STA __div_16u_divisor_buffer

	INY

	LDA (__arg_div_16u_dividend_ptr),Y
	STA __div_16u_dividend_buffer+1
	LDA (__arg_div_16u_divisor_ptr),Y
	STA __div_16u_divisor_buffer+1

	CLD
	LDA #0
	STA __div_16u_quotient
	STA __div_16u_quotient+1

	_DIV_16U_LOOP:
		; compare if dividend is smaller than divisor
		; checks low bytes
		LDA __div_16u_dividend_buffer
		CMP __div_16u_divisor_buffer
		
		LDA __div_16u_dividend_buffer+1
		SBC __div_16u_divisor_buffer+1
	
		; same stuff
		BCC _DIV_16U_END
		
		;------------------------------

		SEC ;just in case

		; subtract divisor from divident
		LDA __div_16u_dividend_buffer
		SBC __div_16u_divisor_buffer
		STA __div_16u_dividend_buffer

		LDA __div_16u_dividend_buffer+1
		SBC __div_16u_divisor_buffer+1
		STA __div_16u_dividend_buffer+1

		CLC
		LDA __div_16u_quotient
		ADC #0x1
		STA __div_16u_quotient

		LDA __div_16u_quotient+1
		ADC #0x0
		STA __div_16u_quotient+1

		JMP _DIV_16U_LOOP

	_DIV_16U_END:
		; store results and 
		; restore registers

		LDY #0

		LDA __div_16u_dividend_buffer
		STA (__arg_div_16u_divisor_ptr),Y
		LDA __div_16u_quotient
		STA (__arg_div_16u_dividend_ptr),Y

		INY

		LDA __div_16u_dividend_buffer+1
		STA (__arg_div_16u_divisor_ptr),Y
		LDA __div_16u_quotient+1
		STA (__arg_div_16u_dividend_ptr),Y

		PLA
		TAY
		PLA
		TAX

		RTS


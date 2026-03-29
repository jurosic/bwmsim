.extern PRINT_UINT16
.org $8000

.res ply, 2
.res crc_out, 2
.res data, 20
.res data_len, 1

_DATA:
	; okay so there is this really
	; funny bug, where labels that
	; are used in an instruction 
	; except branch or jmp increment
	; byte counting wrong, so those 
	; labels have to be defined atop
	;
	; fix later...
	.byte 'H'
	.byte 'e'
	.byte 'l'
	.byte 'l'
	.byte 'o'
	.byte '!'

START:

	; load polynomial
	LDA #0x6E
	STA ply
	LDA #0xF2
	STA ply+1

	; zero crc_out
	LDA #0
	STA crc_out
	STA crc_out+1

	; load data
	; from rom
	LDA #6
	STA data_len

	LDY #0
	FOR_DATA_LOAD_LOOP:
		LDA _DATA,Y
		STA data,Y

		INY

		TYA
		CMP data_len
		
		BMI FOR_DATA_LOAD_LOOP

	; perform crc
	CLC
	CLD
	CLV

	LDX #0
	BYTE_CRC_LOOP:
		LDA crc_out
		EOR data,X
		STA crc_out

		LDY #8
		BIT_CRC_LOOP:
			ASL crc_out
			ROL crc_out+1

			BCC SKIP_XOR

			LDA crc_out+1
			EOR ply+1
			STA crc_out+1

			LDA crc_out
			EOR ply
			STA crc_out

			SKIP_XOR:
			
			DEY 

			TYA
			BNE BIT_CRC_LOOP

		INX

		TXA
		CMP data_len

		BNE BYTE_CRC_LOOP
	
	; print the hash

	LDA >crc_out
	STA 0xFE
	LDA <crc_out
	STA 0xFF

	JSR PRINT_UINT16

	BRK

.org $8000

START:
    LDA #00
    CLC

LOOP:
    ADC #01
	STA 00
	LDA 00
	PHA   
    LDA 00 
	CMP #05
    BEQ FINISH
    JMP LOOP 

FINISH:
    STA FF  
    BRK    

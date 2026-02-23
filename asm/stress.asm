.org $8000

START:
LDA #05 
STA 30
CLD             
CLC             
CLV             


LDA #01 
STA 10 
LDA #0A
STA 11 
LDA #00        
STA 12 

LOOP:
    LDA 12 
    ADC 30
    STA 12
    
    
    LDA 10 
    CLC
    ADC #01
    STA 10 
    
    
    CMP 11 
    BNE LOOP


LDA 12          
PHA             
LDX #FF 
PLA             
TAY             


CPY #00         
BEQ IS_ZERO     
BPL IS_POS      

IS_ZERO:
    LDX #00     
    JMP END     

IS_POS:
    LDX #01     

END:
    BRK

; =======================================================
; THE 16-BIT DIVISION GAUNTLET
; Divides a 16-bit ZP integer by an 8-bit ZP integer.
; Outputs 16-bit Quotient and 8-bit Remainder.
; =======================================================

.org $8000
START:
; --- 1. INITIALIZATION ---
CLD
SEI
LDA #B2
STA 10       ; Dividend Low = 0xB2
LDA #A5
STA 11       ; Dividend High = 0xA5
LDA #37
STA 12       ; Divisor = 0x37 (55)

; --- 2. EXECUTE SUBROUTINE ---
JSR DIVIDE

; --- 3. STORE RESULTS ---
LDA 10
STA $2000    ; Store Quotient Low
LDA 11
STA $2001    ; Store Quotient High
LDA 13
STA $2002    ; Store Remainder

; --- 4. INC/DEC ABSOLUTE MEMORY TEST ---
; Tests if INC/DEC correctly update memory and the N flag
LDA #7F
STA $2003
INC $2003    ; 0x7F + 1 = 0x80 (Negative flag should become 1)
LDA $2003
BMI PASS_INC
JMP FAIL
PASS_INC:
DEC $2003    ; 0x80 - 1 = 0x7F (Negative flag should become 0)
LDA $2003
BPL PASS_DEC
JMP FAIL
PASS_DEC:

; --- 5. STACK & FLAGS PRESERVATION TEST ---
; Tests if PHP and PLP correctly backup and restore the P register
LDA #00      ; Sets Z=1, N=0
CLV          ; Sets V=0
PHP          ; Push flags to stack
LDA #7F
CLC
ADC #02      ; Force overflow (V=1, N=1, Z=0)
PLP          ; Pull flags. Should completely restore Z=1, N=0, V=0!

BVC PASS_V   ; Branch if V=0
JMP FAIL
PASS_V:
BEQ PASS_Z   ; Branch if Z=1
JMP FAIL
PASS_Z:
BPL PASS_N   ; Branch if N=0
JMP FAIL
PASS_N:

; --- 6. SUCCESS ---
LDA #FF
STA $200A    ; Success marker
BRK

FAIL:
LDA #00
STA $200A    ; Failure marker
BRK


; =======================================================
; SUBROUTINE: 16-BIT DIVIDE
; Because you don't have BCC (Branch on Carry Clear), 
; we exploit the fact that a Max Remainder (54) shifted 
; left + 1 is 109. Since 109 < 128, the signed bit is 
; never accidentally triggered! We can perfectly substitute 
; BMI to check if Remainder < Divisor!
; =======================================================
DIVIDE:
LDA #00
STA 13       ; Remainder = 0
LDA #10
STA 14       ; Loop Counter = 0x10 (16 decimal)

DIV_LOOP:
ASL 10       ; Shift Dividend Low left (Bit 7 goes into Carry)
ROL 11       ; Shift Dividend High left (Carry goes into Bit 0)
ROL 13       ; Shift Carry into the Remainder
LDA 13
CMP 12       ; Compare Remainder with Divisor
BMI SKIP_SUB ; If Remainder < Divisor, skip subtraction
SBC 12       ; Remainder >= Divisor. Subtract it! (Carry is guaranteed 1)
STA 13       ; Save new Remainder
INC 10       ; Classic 6502 Trick: Set lowest bit of Dividend to 1 to build Quotient!

SKIP_SUB:
DEC 14       ; Decrement loop counter
BNE DIV_LOOP ; Loop 16 times
RTS

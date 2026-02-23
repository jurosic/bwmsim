.org $8000
; --- 1. INITIALIZATION ---
START:
CLD
SEI
LDA #1A
STA 10     ; ZP 10 (Multiplicand) = 0x1A (26)
LDA #4F
STA 11     ; ZP 11 (Multiplier) = 0x4F (79)

; --- 2. HEAVY MATH CALCULATION ---
; Call subroutine to multiply ZP 10 and ZP 11.
; Result will be placed in ZP 12 (Low Byte) and ZP 13 (High Byte).
JSR MULTIPLY

; --- 3. LOGIC & ABSOLUTE MEMORY TEST ---
LDA 12     
EOR #FF
STA $1000  ; Invert Product Low Byte and store at Absolute $1000

LDA 13
EOR #55
STA $1001  ; XOR Product High Byte with 0x55 and store at Absolute $1001

; --- 4. STACK MANIPULATION ---
LDA #AA
PHA        ; Push 0xAA
LDA #BB
PHA        ; Push 0xBB
PLA
STA 20     ; Pull into ZP 20 (Should be 0xBB)
PLA
STA 21     ; Pull into ZP 21 (Should be 0xAA)

; --- 5. CHAINED LOGIC & SUBTRACTION ---
LDA 20
AND 21     ; 0xBB AND 0xAA = 0xAA
ORA #05    ; 0xAA OR 0x05 = 0xAF
STA 22

SEC
LDA 22
SBC #A0    ; 0xAF - 0xA0 = 0x0F
STA $1002  ; Store at Absolute $1002

; --- 6. FLAG & BRANCHING GAUNTLET ---
; Test BIT instruction (Sets N flag to bit 7 of memory)
LDA #80
STA 23
LDA #FF
BIT 23     ; 0x80 has bit 7 high, so Negative (N) flag becomes 1
BMI TEST_OVERFLOW
JMP FAIL

TEST_OVERFLOW:
CLV
LDA #7F
CLC
ADC #02    ; 0x7F + 0x02 = 0x81 (Crosses 127 boundary, V flag becomes 1)
BVS TEST_COMPARES
JMP FAIL

TEST_COMPARES:
LDX #10
CPX #10    ; 0x10 == 0x10 (Z flag becomes 1)
BNE FAIL
LDY #20
CPY #15    ; 0x20 - 0x15 = 0x0B (Result is positive, N flag is 0)
BPL SUCCESS
JMP FAIL

; --- 7. TERMINATION ---
FAIL:
LDA #00
STA $1003  ; Store 0x00 on fail
BRK

SUCCESS:
LDA #FF
STA $1003  ; Store 0xFF on success
BRK


; =========================================
; SUBROUTINE: 16-BIT MULTIPLY (Shift & Add)
; Multiplies ZP 10 by ZP 11. 
; Outputs to ZP 12 (Low) and ZP 13 (High).
; =========================================
MULTIPLY:
LDA #00
STA 12     ; Clear Product Low
STA 13     ; Clear Product High
STA 16     ; Clear Temp High multiplicand
LDA #08
STA 14     ; Set Loop Counter to 8
LDA 10
STA 15     ; Copy Multiplicand to Temp Low

MULT_LOOP:
LDA 11
AND #01    ; Check lowest bit of multiplier
BEQ SKIP_ADD

; If bit is 1, Add shifted multiplicand to product
LDA 12
CLC
ADC 15
STA 12
LDA 13
ADC 16
STA 13

SKIP_ADD:
LSR 11     ; Shift Multiplier Right
ASL 15     ; Shift Multiplicand Low Left
ROL 16     ; Rotate Multiplicand High Left (catches carry from ASL 15)
DEC 14     ; Decrement loop counter
BNE MULT_LOOP
RTS

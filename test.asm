; ==========================================
; TEST: Count to 5
; Tests: Labels, Immediate Mode, Absolute Jumps
; ==========================================

START:
    LDA #$00      ; Initialize Accumulator to 0
    CLC           ; Clear Carry before math

LOOP:
    ADC #$01      ; Add 1 to Accumulator
    CMP #$05      ; Compare Accumulator to 5
    BEQ FINISH    ; If Equal (Z=1), go to FINISH
    JMP LOOP      ; Else, Jump back to LOOP

FINISH:
    STA $FF       ; Store the result (5) in address 255
    BRK           ; Stop execution
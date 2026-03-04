.org $8000

.res first, 255
.res second, 1
.equ this_should_warn, $0xFFFE
START:
	LDA #10
	STA first
	.rel second
	.res ssecond, 1
	LDA #200
	STA ssecond
	LDA #30
	STA ssecond

	BRK


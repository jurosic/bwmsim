.org $8000

.res first, 254
.res second, 1
START:
	LDA #10
	STA first
	.rel first
	.res ffirst, 1
	LDA #200
	STA second
	LDA #30
	STA ffirst
	.rel sksk

	BRK


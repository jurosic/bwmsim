.extern print

.org $8000

START:
	!
	JSR skp
		skp:
	LDA <HELLO
	PHA
	LDA >HELLO
	PHA
	LDA #6
	PHA

	JMP PRINT

	JSR skp2
		skp2:
	LDA <WORLD
	PHA
	LDA >WORLD
	PHA
	LDA #7
	PHA

	JMP PRINT

	BRK

HELLO:
	.byte 'H'
	.byte 'e'
	.byte 'l'
	.byte 'l'
	.byte 'o'
	.byte '\n'

WORLD:
	.byte 'W'
	.byte 'o'
	.byte 'r'
	.byte 'l'
	.byte 'd'
	.byte '!'
	.byte '\n'

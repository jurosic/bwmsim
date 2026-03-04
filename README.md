# bwmsim is an SY6502 simulator made in python

## What is this even about?
This is a from scratch project that features a barebones digital circuit simulation library, SY6502 assembler/compiler, as well as multiple chips that have their logic emulated in python.

For now these chips are:
`SY6502`   - 90% functional <br>
`CY62256N` - 100% functional <br>
`AT28C256` - 100% functional <br>
`74HTC138` - 100% functional <br>

### zeusammen
The assembler/compiler is mostly just vibecoded for now, but features a custom syntax:
1. **Instruction Names**
   - names of the instructions are the same as in the reference material datasheet
2. **Addressing Modes**
   - the assembler/compiler supports all SY6502 addressing modes with the following syntax:
       1. Immediate
          - loads the byte right after this instruction
          - prefixed with `#`
       2. Absolute
          - loads the byte at the absolute memory address (2 bytes)
          - prefixed with `$`
       3. ZeroPage
          - loads the byte at the zeropage memory address (1 byte)
          - has **NO** prefix
          - faster than Absolute but should probably only be used for pointers and arguments
       4. Absolute Indexed
          - loads the byte at the absolute memory address incremented by the X or Y register
          - syntax: `$[address],X` or `$[address],Y`
       5. ZeroPage Indexed
          - loads the byte at the zeropage memory address incremented by the X or Y register
          - syntax: `[addresss],X` or `[address],Y`
          - once again faster than absolute
       6. Indexed Indirect
          - loads the byte where the zeropage address incremented by X points to
          - *OR*
          - loads the byte at the address that the zeropage address points to incremented by Y
          - syntax: `([address],X)` or `([address]),Y`
3. **Labels**
   - as it should, the compiler/assembler supports labels
   - labels are defined by a `:` suffix like so: `START:`
   - labels can be put into the argument of any function just by their name like so: `JMP START`
4. **Directives**
   1. equ
      - this directive is used to define constants
      - constants are drop in replacements for their name meaning they have to have an addressing mode in them
      - defining a constant can be done like so: `.equ name, value`
      - they can be defined anywhere in the code and are available globally
      - they do not follow any scopes
      - the compiler may warn about duplicate constants if the right strictness is set
   2. res
      - this directive is used to define a variable the memory location of which is automatically determined by the compiler
      - creating a var can be done like so: `.res name, size`
      - they act similar to constants
   3. rel
      - this directive is used to release a variable 
      - releasing a var can be done like so: `.rel name`
   4. ignore
      - writing `.ignore` **above** the directive makes the compiler ignore any warnings or errors that directive could have caused
   5. extern
      - adds an external code file to the current file at preprocessing, used for libraries
      - used like so: `.extern print`
      - adds `print.asm` **at the top** of the program the `.extern` is written in
   6. byte
      - signals the compiler to write a raw byte at the current location
      - `.byte 'H'`
   7. org
      - tells the compiler what address the program should start at
      - `.org $8000`
5. **Different numeric bases**
   - the compiler supports base 10 (no prefix), base 2 (0b prefix) and base 16 (0x prefix)
6. **Compiler Warnings and Strictness**
   - the compiler has some warnings in place, the strictness about these can be set with the `-S` argument
   - you can also treat all warnings as errors using the `-werr` flag

For more information about the compiler run:
`python zeusammen.py --help`

The main purpose of this project is simulating an SY6502 CPU down at the 'almost' hardware level, to (hopefully) ease the process of creating a physical version.

**THIS PROJECT IS FAR FROM FINISHED, THINGS ARE STILL VERY BUGGY**

## How to implement your own chip
**bwmsim** simulates down to the hardware level, using a custom library `ele.py` \\
adding your own chip is as simple as writing some code that works with `ele.py`'s `Pin` or `Group` classes

```python
class Testchip():
  def __init__(self):
    self.bus = Group(8) #creates an 8bit bus

  def update(self):
    ..code that uses self.bus..
```

these chips can then be connected together like so

```python
chip1 = Testchip()
chip2 = Testchip()

chip1.bus.connect(chip2.bus) #connects the two busses together
```

connections are always bidirectional and create a mesh-like structure. for example:

```python
chip1 = Testchip()
chip2 = Testchip()
chip3 = Test...
chip4 = ...
...

#connect

chip1.bus.connect(chip2.bus)
chip2.bus.connect(chip3.bus)
chip3.bus.conn....
chip4...
....
```

all these connections will be recursively meshed together, meaning that if any chip sends a signal, all the chips recieve it without them needing to be implicitly connected together.

to send a signal into the network you can just do 

```python
chip1.bus.signal([True, False, True] + [False for _ in range(0,5)])

chip2.bus.state
>>[True, False, True, False, False, False, False, False]
```

since `Group` uses `Pin` inside of its code, pins work in the same exact way, the only difference is that signals are `bool` instead of `list[bool]`

```python
pin1 = Pin()
pin2 = Pin()

pin1.connect(pin2)

pin2.signal(True)

pin1.state
>> True
```

# Resources:
[Instruction Set](http://www.6502.org/users/obelisk/6502/reference.html) \\
[SY6502 PDF](https://github.com/jurosic/bwmsim/blob/main/resources/SY6502.pdf) \\
[CY62265N PDF](https://github.com/jurosic/bwmsim/blob/main/resources/CY62256N.pdf) \\
[AT28C256 PDF](https://github.com/jurosic/bwmsim/blob/main/resources/AT28C256.pdf) \\


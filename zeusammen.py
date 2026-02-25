"""
example code:
    
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
"""

import sys

#BEHAVIOR FLAGS
TEST_OUTPUT = False

ORIGIN = 0x0000
LIBS = []

SYMTABLE = {}

INST_TABLE = {
        "ADC": { "imm": 0x69, "abs": 0x6d, "zp": 0x65 },
        "AND": { "imm": 0x29, "abs": 0x2d, "zp": 0x25 },
        "ASL": { "abs": 0x0e, "zp": 0x06 },
        "BCC": { "rel": 0x90 },
        "BCS": { "rel": 0xB0 },
        "BEQ": { "rel": 0xef },
        "BIT": { "abs": 0x2c, "zp": 0x24 },
        "BMI": { "rel": 0x30 },
        "BNE": { "rel": 0xd0 },
        "BPL": { "rel": 0x10 },
        "BRK": { "imp": 0x00 },
        "BVC": { "rel": 0x50 },
        "BVS": { "rel": 0x70 },
        "CLC": { "imp": 0x18 },
        "CLD": { "imp": 0xd8 },
        "CLI": { "imp": 0x58 },
        "CLV": { "imp": 0xB8 },
        "CMP": { "imm": 0xc9, "abs": 0xcd, "zp": 0xc5 },
        "CPX": { "imm": 0xe0, "abs": 0xce, "zp": 0xe4 },
        "CPY": { "imm": 0xc0, "abs": 0xcc, "zp": 0xe4 },
        "DEC": { "abs": 0xce, "zp": 0xc6 },
        "DEX": { "imp": 0xca },
        "DEY": { "imp": 0x88 },
        "EOR": { "imm": 0x49, "abs": 0x4d, "zp": 0x45 },
        "INC": { "abs": 0xee, "zp": 0xe6 },
        "INX": { "imp": 0xE8 },
        "INY": { "imp": 0xC8 },
        "JMP": { "abs": 0x4c },
        "JSR": { "abs": 0x20 },
        "LDA": { "imm": 0xa9, "abs": 0xad, "zp": 0xa5 },
        "LDX": { "imm": 0xa2, "abs": 0xae, "zp": 0xa6 },
        "LDY": { "imm": 0xa0, "abs": 0xac, "zp": 0xa4 },
        "LSR": { "abs": 0x4e, "zp": 0x46 },
        "NOP": { "imp": 0xea },
        "ORA": { "imm": 0x09, "abs": 0x0d, "zp": 0x05 },
        "PHA": { "imp": 0x48 },
        "PHP": { "imp": 0x08 },
        "PLA": { "imp": 0x68 },
        "PLP": { "imp": 0x28 },
        "ROL": { "abs": 0x2e, "zp": 0x26 },
        "ROR": { "abs": 0x6e, "zp": 0x66 },
        "RTI": { "imp": 0x40 },
        "RTS": { "imp": 0x60 },
        "SBC": { "imm": 0xe9, "abs": 0xed, "zp": 0xe5 },
        "SEC": { "imp": 0x38 },
        "SED": { "imp": 0xf8 },
        "SEI": { "imp": 0x78 },
        "STA": { "abs": 0x8d, "zp": 0x85 },
        "STX": { "abs": 0x8e, "zp": 0x86 },
        "STY": { "abs": 0x8c, "zp": 0x84 },
        "TAX": { "imp": 0xaa },
        "TAY": { "imp": 0xa8 },
        "TSX": { "imp": 0xBA },
        "TXA": { "imp": 0x8a },
        "TXS": { "imp": 0x9A },
        "TYA": { "imp": 0x98 },
        "!"  : { "imp": 0x67 }
    }


class StartUndefined(Exception):
    pass

class LibDirUndefined(Exception):
    pass

class SymbolRedefinitionError(Exception):
    pass

def _inst_to_byte(inst: list[str], pos=0): 
    """
        Converts an instruction into a list of bytes

    Args:
        inst (list[str]): instruction to be converted
    """
    
    if inst[0].upper() not in INST_TABLE.keys():
        print(f"Invalid instruction {inst[0]}")
        exit(1)

    inst_name = inst[0].upper()
    if len(inst) == 1:
        #implied
        return [INST_TABLE[inst_name]["imp"]]
    elif len(inst) == 2:
        #not a very robust way to check for rel addresses.
        if inst[0].upper() in ["BEQ", "BMI", "BNE", "BPL", "BVS", "BVC", "BCS", "BCC"]:
            #relative
            offset = int(inst[1][1:], 16) - pos - ORIGIN  # +2 because the instruction is 2 bytes long
            #print(f"Calculating relative offset for {inst[1]}: {int(inst[1][1:], 16)} - {pos} - {ORIGIN} = {offset}")
            return [INST_TABLE[inst_name]["rel"], offset]
        elif inst[1].startswith("#"):
            #immediate
            return [INST_TABLE[inst_name]["imm"], int(inst[1][1:], 16)]
        elif inst[1].startswith("$"):
            #absolute
            return [INST_TABLE[inst_name]["abs"], int(inst[1][1:], 16) & 0xFF, (int(inst[1][1:], 16) >> 8) & 0xFF]
        else:
            #zero page
            return [INST_TABLE[inst_name]["zp"], int(inst[1], 16)]
    else:
        print(f"Invalid instruction format for {inst}")
        exit(1)            


def _argsan(args: list[str]):
    """
        Checks if args supplied are valid

    Args:
        args (list[str]): Arguments
    """
    
    if len(args) < 2:
        _help()
        exit(1)
        
    match args[1]:
        case "cmp":
            #check if outfile is supplied
            if len(args) < 4:
                print("Please supply an output file.")
                exit(1)

def _help():
    print('\n'.join((
        "ZEUSAMMEN is a compiler from assembly into the SY6502 instruction set",
        "Example usage:",
        "\t python zeusammen.py cmp [infile] [outfile] [libdir]",

        "",
        "Or if youd like to see how the file looks after processing",
        "Add the -to flag"
    )))
    
def sanitize(line: str) -> list[str]:
    """
        Checks for invalid input and removes comments
        Breaks up lines into individual bytes

    Args:
        line (string): line of code to be sanitized
    """
    
    cmt_start: int = len(line)
    if ";" in line:
        cmt_start = line.index(";")
    if ".extern" in line:
        return [""]
    
    #truncate without comment
    #split into bytes
    cde = line[:cmt_start]
    cde = cde.strip()
    cde = cde.split(" ")
    
    return cde

def symbolize(prog: list[list[str]]):
    """
        Symbolizes labels into memory locations

    Args:
        prog (list[list[str]]):

    Raises:
        StartUndefined: Raised if the program lacks a START label
    """
    
    global SYMTABLE
    
    byte_ctr: int = 0
    
    #pass 1
    for inst in prog:
        if inst[0].endswith(":"):
            #symbol definiton here
            if inst[0].strip(':') in SYMTABLE:
                raise SymbolRedefinitionError(f"Symbol {inst[0].strip(':')} is being redefined!")
            SYMTABLE[inst[0].strip(":")] = "$" + str(hex(byte_ctr + ORIGIN))[2:].upper()
        elif inst[0].upper() in ["BEQ", "BMI", "BNE", "BPL", "BVS", "BVC", "BCS", "BCC"]:
            #relative branch, 2 bytes
            byte_ctr += 2
        elif inst[0].upper() in ["JMP", "JSR"]:
            #absolute jump, 3 bytes
            byte_ctr += 3
        else:
            #add instruction byte
            byte_ctr += 1
            #check length of the arg (1 byte or 2 bytes)
            if len(inst) > 1:
                if inst[1].startswith("$"):
                    #absolute, 2 bytes
                    byte_ctr += 2
                else:
                    #zero page or immediate 1 byte
                    byte_ctr += 1

    #remove any labels from the program
    plen = len(prog)
    while plen > 0:
        plen -= 1
        i = len(prog) - plen - 1
        if len(prog[i]) == 1 and prog[i][0].endswith(":"):
            prog.pop(i)

    #remove any empty lines
    for i in range(len(prog)):
        if prog[i] == []:
            prog.pop(i)

    #check for start, more efficient this way than uppering or lowering
    if "start" not in SYMTABLE.keys() and "START" not in SYMTABLE.keys():
        raise StartUndefined("The program has no start!")

def preprocess(prog: list[list[str]]):
    global SYMTABLE
    """
        Replaces things like variable names or labels with memory locations

    Args:
        prog (list[list[str]]): 
    """
    
    #now we replace
    for inst in prog:
        for i in range(len(inst)):
            if inst[i] in SYMTABLE.keys():
                #print(f"Replacing symbol {inst[i]} with {SYMTABLE[inst[i]]}")
                inst[i] = SYMTABLE[inst[i]]
   
    #convert instructions to bytes
    byte_cnter = 0
    for i in range(len(prog)):
        if prog[i][0].endswith(":"):
            continue #if by SOME CHANCE there are still labels, skip them
        #handle possible absolute args for byte_cnter
        if len(prog[i]) > 1:
            if prog[i][1].startswith("$") and prog[i][0].upper() not in ["BEQ", "BMI", "BNE", "BPL", "BVS"]:
                byte_cnter += 2
            else:
                byte_cnter += 1
        byte_cnter += 1
        prog[i] = _inst_to_byte(prog[i], byte_cnter)


def write_bytes(prog: list[list[int]], outfile: str):
    """
        Writes the program to a file

    Args:
        prog (list[list[int]]): program to be written
        outfile (str): output file
    """
    wrote_reset_vector = False   
    with open(outfile, "wb") as f:
        i = 0
        byte_cnter = 0
        while True:
            if byte_cnter >= 32_768:
                break

            if i < len(prog):
                for byte in prog[i]:
                    num_bytes = (byte.bit_length() + 7) // 8 or 1
                    #print(f"{num_bytes} bytes for {byte}")
                    signed = byte < 0
                    f.write(byte.to_bytes(num_bytes, "little", signed=signed))
                    byte_cnter += num_bytes  
                i += 1
            elif byte_cnter > 32_761 and not wrote_reset_vector:
                print("Writing reset vector...")
                #write the reset vector
                f.write((0x4C).to_bytes(1, "little"))
                num_bytes = (ORIGIN.bit_length() + 7) // 8 or 1
                f.write(ORIGIN.to_bytes(num_bytes, "little"))
                byte_cnter += num_bytes + 1
                wrote_reset_vector = True
            else:
                f.write((0).to_bytes(1, "little"))
                byte_cnter += 1

def import_libs(prog, lib_dir= None):
    for lib in LIBS:
        if lib_dir == None:
            raise LibDirUndefined
        with open(lib_dir.strip("/") + '/' +lib, "r") as lf:
            for line in lf:
                san = sanitize(line)
                if san != [""]:
                    prog.append(san)

def recurse_libs(asmfile: str, lib_dir: str):
    with open(asmfile, "r") as f:
        for line in f:
            if line.startswith(".extern"):
                libn = line.split(" ")[1].strip() + ".asm"
                #cut libdir if in name
                libn = libn.split("/")[-1]
                libnn = lib_dir.strip("/") + "/" + libn
                recurse_libs(libnn, lib_dir)
                if libn not in LIBS:
                    LIBS.append(libn)
    
def rn_cmp(infile: str, outfile: str, lib_dir: str):
    global SYMTABLE
    global ORIGIN   
    """
        Essentially a function that gathers all the steps in the compilation process

    Args:
        infile (str): input file
        outfile (str): output file
    """
    
    sanitized: list = []
    with open(infile, "r") as f:
        for line in f:
            if line.startswith("."):
                if line.startswith(".org"):
                    ORIGIN = int(line.split(" ")[1][1:], 16)
                continue

            if any((line.strip() == "",
                   line.startswith(";"),
                   line.startswith("\n"))):
                continue

            san = sanitize(line)
            if san != [""]:
                sanitized.append(san)

    recurse_libs(infile, lib_dir)
    import_libs(sanitized, lib_dir)
   
    if TEST_OUTPUT:
        with open(infile.split("/")[-1] + ".to", "w+") as f:
            for eline in sanitized:
                f.write(' '.join(eline) + '\n')
        print("dumped debug output")
        return

    symbolize(sanitized)

    #print("Symbol Table:")
    #for k in SYMTABLE.keys():
    #    print(f"\t{k} : {SYMTABLE[k]}")
    #print(sanitized)

    preprocess(sanitized)

    #print(sanitized)
    #print(SYMTABLE)

    write_bytes(sanitized, outfile)

    byte_len = 0
    for inst in sanitized:
        byte_len += len(inst)
    print('\n'.join((
            f"Wrote: {len(sanitized)} instructions, totalling {byte_len} bytes.",
            f"thats {(byte_len/(2**16))*100:.2f}% of 16bit addressing",
            f"or    {(byte_len/(2**15))*100:.2f}% of 15bit addressing",
        )))


if __name__ == "__main__":
    args = sys.argv
    
    _argsan(args)

    #check for flags
    for arg in args:
        if arg == '-to':
            TEST_OUTPUT = True

    #essentially running match twice but whatever
    match args[1]:
        case "cmp":
            rn_cmp(args[2], args[3], args[4])
        
        case _:
            _help()
            exit(1)

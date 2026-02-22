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

ORIGIN = 0x0000

SYMTABLE = {}

INST_TABLE = {
        "ADC": {
            "imm": 0x69,
            "zp": 0x65,
            "abs": 0x6D
        },
        "AND": {
            "imm": 0x29,
            "zp": 0x25,
            "abs": 0x2D
        },
        "BEQ": {
            "rel": 0xEF
        },
        "BMI": {
            "rel": 0x30
        },
        "BNE": {
            "rel": 0xD0
        },
        "BPL": {
            "rel": 0x10
        },
        "BRK": {
            "imp": 0x00
        },
        "BVS": {
            "rel": 0x70
        },
        "CLC": {
            "imp": 0x18
        },
        "CLD": {
            "imp": 0xD8
        },
        "CLI": {
            "imp": 0x58
        },
        "CLV": {
            "imp": 0x88
        },
        "CMP": {
            "imm": 0xC9
        },
        "CPX": {
            "imm": 0xE0
        }, "CPY": {
            "imm": 0xC0
        },
        "JMP": {
            "abs": 0x4C
        },
        "LDA": {
            "imm": 0xA9,
            "zp": 0xA5
        },
        "LDX": {
            "imm": 0xA2,
            "zp": 0xA6
        },
        "LDY": {
            "imm": 0xA0
        },
        "PHA": {
            "imp": 0x48
        },
        "PLA": {
            "imp": 0x68
        },
        "STA": {
            "zp": 0x85
        },
        "STX": {
            "zp": 0x86
        },
        "TAX": {
            "imp": 0xAA
        },
        "TAY": {
            "imp": 0xA8
        },
        "TXA": {
            "imp": 0x8A
        },
        "TYA": {
            "imp": 0x98
        }
}        



class StartUndefined(Exception):
    pass

def _inst_to_byte(inst: list[str], pos=0): 
    """
        Converts an instruction into a list of bytes

    Args:
        inst (list[str]): instruction to be converted
    """
    
    match inst[0].upper():
        case "ADC":
            if inst[1].startswith("#"):
                return [INST_TABLE["ADC"]["imm"], int(inst[1][1:], 16)]
            elif inst[1].startswith("$"):
                return [INST_TABLE["ADC"]["abs"], int(inst[1][1:], 16)]
            else:
                return [INST_TABLE["ADC"]["zp"], int(inst[1], 16)]
        
        case "AND":
            if inst[1].startswith("#"):
                return [INST_TABLE["AND"]["imm"], int(inst[1][1:], 16)]
            elif inst[1].startswith("$"):
                return [INST_TABLE["AND"]["abs"], int(inst[1][1:], 16)]
            else:
                return [INST_TABLE["AND"]["zp"], int(inst[1], 16)]
        
        case "BEQ":
            print(f"Calculating relative address for {inst[1]} at position {pos} with origin {ORIGIN}")
            return [INST_TABLE["BEQ"]["rel"], int(inst[1][1:], 16) - ORIGIN - pos + 1]
         
        case "BMI":
            return [INST_TABLE["BMI"]["rel"], int(inst[1][1:], 16) - ORIGIN - pos + 1]
        
        case "BNE":
            return [INST_TABLE["BNE"]["rel"], int(inst[1][1:], 16) - ORIGIN - pos + 1]
        
        case "BPL":
            return [INST_TABLE["BPL"]["rel"], int(inst[1][1:], 16) - ORIGIN - pos + 1]
        
        case "BRK":
            return [INST_TABLE["BRK"]["imp"]]
        
        case "BVS":
            return [INST_TABLE["BVS"]["rel"], int(inst[1][1:], 16) - ORIGIN - pos + 1]
        
        case "CLC":
            return [INST_TABLE["CLC"]["imp"]]
        
        case "CLD":
            return [INST_TABLE["CLD"]["imp"]]
        
        case "CLI":
            return [INST_TABLE["CLI"]["imp"]]
        
        case "CLV":
            return [INST_TABLE["CLV"]["imp"]]
        
        case "CMP":
            if inst[1].startswith("#"):
                return [INST_TABLE["CMP"]["imm"], int(inst[1][1:], 16)]
        
        case "CPX":
            if inst[1].startswith("#"):
                return [INST_TABLE["CPX"]["imm"], int(inst[1][1:], 16)]
        case "CPY":
            if inst[1].startswith("#"):
                return [INST_TABLE["CPY"]["imm"], int(inst[1][1:], 16)]
        case "JMP":
            if inst[1].startswith("$"):
                return [INST_TABLE["JMP"]["abs"], int(inst[1][1:], 16)]
        case "LDA":
            if inst[1].startswith("#"):
                return [INST_TABLE["LDA"]["imm"], int(inst[1][1:], 16)]
            elif inst[1].startswith("$"):
                return [INST_TABLE["LDA"]["abs"], int(inst[1][1:], 16)]
            else:
                return [INST_TABLE["LDA"]["zp"], int(inst[1], 16)]
        case "LDX":
            if inst[1].startswith("#"):
                return [INST_TABLE["LDX"]["imm"], int(inst[1][1:], 16)]
            else:
                return [INST_TABLE["LDX"]["zp"], int(inst[1], 16)]
        case "LDY":
            if inst[1].startswith("#"):
                return [INST_TABLE["LDY"]["imm"], int(inst[1][1:], 16)]
        case "PHA":
            return [INST_TABLE["PHA"]["imp"]]
        case "PLA":
            return [INST_TABLE["PLA"]["imp"]]
        case "STA":
            if inst[1].startswith("$"):
                return [INST_TABLE["STA"]["abs"], int(inst[1][1:], 16)]
            else:
                return [INST_TABLE["STA"]["zp"], int(inst[1], 16)]
        case "STX":
            if inst[1].startswith("$"):
                return [INST_TABLE["STX"]["abs"], int(inst[1][1:], 16)]
            else:
                return [INST_TABLE["STX"]["zp"], int(inst[1], 16)]
        case "TAX":
            return [INST_TABLE["TAX"]["imp"]]
        case "TAY":
            return [INST_TABLE["TAY"]["imp"]]
        case "TXA":
            return [INST_TABLE["TXA"]["imp"]]
        case "TYA":
            return [INST_TABLE["TYA"]["imp"]]
        case _:
            print(f"Unknown instruction: {inst[0]}")
            raise Exception("Unknown instruction")
            


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
        "\t python zeusammen.py cmp [infile] [outfile]"
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
    
    for inst in prog:
        if inst[0].endswith(":"):
            #symbol definiton here
            SYMTABLE[inst[0].strip(":")] = "$" + str(hex(byte_ctr + ORIGIN))[2:].upper()
        else:
            byte_ctr += len(inst)

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
    
    byte_cnter = 0
   
    #first we shift
    for inst in prog:
        for i in range(len(inst)):
            if inst[i] in SYMTABLE.keys():
                #if the inst is a branch, this is before relative addresses
                #are calculated, so we need to add an exception for them
                if '$' in SYMTABLE[inst[i]] and inst[0].upper() not in ["BEQ", "BMI", "BNE", "BPL", "BVS"]:
                    #some args are 2 bytes
                    byte_cnter += 1
                    print(f"Symbol {SYMTABLE[inst[i]]} is a memory address, adding 1 to instruction length")
                    #we need to offset labels to account for this 
                    for k in SYMTABLE.keys():
                        if int(SYMTABLE[k][1:], 16) > byte_cnter + ORIGIN:
                            print(f"{byte_cnter} + {ORIGIN} + {1} = {byte_cnter + ORIGIN + 1}")
                            print(f"Shifting symbol {k} from {SYMTABLE[k]} to ", end="")
                            print(f"{'$' + str(hex(int(SYMTABLE[k][1:], 16) + 1))[2:].upper()} because it is after the current instruction")
                            SYMTABLE[k] = "$" + str(hex(int(SYMTABLE[k][1:], 16) + 1))[2:].upper()
        byte_cnter += len(inst)

    byte_cnter = 0
    #now we replace
    for inst in prog:
        for i in range(len(inst)):
            if inst[i] in SYMTABLE.keys():
                print(f"Replacing symbol {inst[i]} with {SYMTABLE[inst[i]]}")
                inst[i] = SYMTABLE[inst[i]]
   
    print("Symbol table after preprocessing:")
    for k in SYMTABLE.keys():
        print(f"\t{k} : {SYMTABLE[k]}")

    #convert instructions to bytes
    byte_cnter = 0
    for i in range(len(prog)):
        byte_cnter += len(prog[i])
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
                    print(f"{num_bytes} bytes for {byte}")
                    f.write(byte.to_bytes(num_bytes, "little"))
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
    
def rn_cmp(infile: str, outfile: str):
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
    
    symbolize(sanitized)

    print("Symbol Table:")
    for k in SYMTABLE.keys():
        print(f"\t{k} : {SYMTABLE[k]}")
    print(sanitized)

    preprocess(sanitized)

    print(sanitized)
    print(SYMTABLE)

    write_bytes(sanitized, outfile)



if __name__ == "__main__":
    args = sys.argv
    
    _argsan(args)

    #essentially running match twice but whatever
    match args[1]:
        case "cmp":
            rn_cmp(args[2], args[3])
        
        case _:
            _help()
            exit(1)

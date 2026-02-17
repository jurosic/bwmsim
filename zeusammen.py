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

SYMTABLE = {}

class StartUndefined(Exception):
    pass

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
    cde: str = line[:cmt_start]
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
        if len(inst) != 1:
            byte_ctr += len(inst)
            continue
        
        if inst[0].endswith(":"):
            #symbol definiton here
            SYMTABLE[inst[0].strip(":")] = byte_ctr
            
        byte_ctr += len(inst)

    #check for start, more efficient this way than uppering or lowering
    if "start" not in SYMTABLE.keys() and "START" not in SYMTABLE.keys():
        raise StartUndefined("The program has no start!")
    
def preprocess(prog: list[list[str]]):
    """
        Replaces things like variable names or labels with memory locations

    Args:
        prog (list[list[str]]): 
    """
    
    byte_cnter = 0
    
    for inst in prog:
        pass
    
def rn_cmp(infile: str, outfile: str):
    global SYMTABLE
    """
        Essentially a function that gathers all the steps in the compilation process

    Args:
        infile (str): input file
        outfile (str): output file
    """
    
    sanitized: list = []
    with open(infile, "r") as f:
        for line in f:
            san: str = sanitize(line)
            if san != [""]:
                sanitized.append(san)
    
    symbolize(sanitized)



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
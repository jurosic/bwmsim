import sys
import warnings

#BEHAVIOR FLAGS
TEST_OUTPUT = False
STRICTNESS = 1
OUTPUT_FILE = "a.bin"
WARN_AS_ERRORS = False
LIB_DIR = None
DYN_MEM_START = int("0x7F00", 16)
DYN_MEM_END = int("0x7FFF", 16) 
DUMP_DF = False

ORIGIN = 0x0000

LIBS = []

LABELS = {}
CONSTANTS = {}
VARIABLES = {}
"""
    name: { 
        "addr": addr,
        "size": size,
        "scope": null | int,
        "released": true | false
    }
"""


INST_TABLE = {
        "ADC": { "imm": 0x69, "abs": 0x6d, "zp": 0x65, "indx": 0x61, "indy": 0x71, "zpx": 0x75, "absx": 0x7D, "absy": 0x79 },
        "AND": { "imm": 0x29, "abs": 0x2d, "zp": 0x25, "indx": 0x21, "indy": 0x31, "zpx": 0x35, "absx": 0x3D, "absy": 0x39 },
        "ASL": { "abs": 0x0e, "zp": 0x06, "imp": 0x0A, "zpx": 0x16, "absx": 0x1E },
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
        "CMP": { "imm": 0xc9, "abs": 0xcd, "zp": 0xc5, "indx": 0xC1, "indy": 0xD1, "zpx": 0xD5, "absx": 0xDD, "absy": 0xD9 },
        "CPX": { "imm": 0xe0, "abs": 0xce, "zp": 0xe4 },
        "CPY": { "imm": 0xc0, "abs": 0xcc, "zp": 0xe4 },
        "DEC": { "abs": 0xce, "zp": 0xc6, "zpx": 0xD6, "absx": 0xDE },
        "DEX": { "imp": 0xca },
        "DEY": { "imp": 0x88 },
        "EOR": { "imm": 0x49, "abs": 0x4d, "zp": 0x45, "indx": 0x41, "indy": 0x51, "zpx": 0x55, "absx": 0x5D, "absy": 0x59 },
        "INC": { "abs": 0xee, "zp": 0xe6, "zpx": 0xF6, "absx": 0xFE },
        "INX": { "imp": 0xE8 },
        "INY": { "imp": 0xC8 },
        "JMP": { "abs": 0x4c, "ind": 0x6C },
        "JSR": { "abs": 0x20 },
        "LDA": { "imm": 0xa9, "abs": 0xad, "zp": 0xa5, "indx": 0xA1, "indy": 0xB1, "zpx": 0xB5, "absx": 0xBD, "absy": 0xB9 },
        "LDX": { "imm": 0xa2, "abs": 0xae, "zp": 0xa6, "absy": 0xBE, "zpy": 0xB6 },
        "LDY": { "imm": 0xa0, "abs": 0xac, "zp": 0xa4, "zpx": 0xB4, "absx": 0xBC },
        "LSR": { "abs": 0x4e, "zp": 0x46, "imp": 0x4A, "zpx": 0x56, "absx": 0x5E },
        "NOP": { "imp": 0xea },
        "ORA": { "imm": 0x09, "abs": 0x0d, "zp": 0x05, "indx": 0x01, "indy": 0x11, "zpx": 0x15, "absx": 0x1D, "absy": 0x19 },
        "PHA": { "imp": 0x48 },
        "PHP": { "imp": 0x08 },
        "PLA": { "imp": 0x68 },
        "PLP": { "imp": 0x28 },
        "ROL": { "abs": 0x2e, "zp": 0x26, "imp": 0x2A, "zpx": 0x36, "absx": 0x3E },
        "ROR": { "abs": 0x6e, "zp": 0x66, "imp": 0x6A, "zpx": 0x76, "absx": 0x7E },
        "RTI": { "imp": 0x40 },
        "RTS": { "imp": 0x60 },
        "SBC": { "imm": 0xe9, "abs": 0xed, "zp": 0xe5, "indx": 0xE1, "indy": 0xF1, "zpx": 0xF5, "absx": 0xFD, "absy": 0xF9 },
        "SEC": { "imp": 0x38 },
        "SED": { "imp": 0xf8 },
        "SEI": { "imp": 0x78 },
        "STA": { "abs": 0x8d, "zp": 0x85, "indx": 0x81, "indy": 0x91, "zpx": 0x95, "absx": 0x9D, "absy": 0x99 },
        "STX": { "abs": 0x8e, "zp": 0x86, "zpy": 0x96 },
        "STY": { "abs": 0x8c, "zp": 0x84, "zpx": 0x94 }, 
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

class DoubleConstDefWarning(Warning):
    pass

class DangerousArgWarning(Warning):
    pass

class ConstInDynMemWarning(Warning):
    pass

class OutOfMemoryError(Exception):
    pass

class VarUndefinedError(Exception):
    pass

class WriteAfterRelease(Exception):
    pass

def _inst_to_byte(inst: list[str], pos=0): 
    """
        Converts an instruction into a list of bytes

    Args:
        inst (list[str]): instruction to be converted
    """
    
    if inst[0].upper() not in INST_TABLE.keys() and inst[0].lower() not in [".byte"]:
        print(f"Invalid instruction {inst[0]}")
        exit(1)

    inst_name = inst[0].upper()
    if len(inst) == 1:
        #implied (acc is treated as imp too)
        return [INST_TABLE[inst_name]["imp"]]
    elif len(inst) == 2:
        #wild, check for .byte definition
        if inst[0].lower() == ".byte":
            #another vibecoded check
            if inst[1].startswith("'") and inst[1].endswith("'"):
                #char
                return [ord(inst[1].replace("'", "").encode("utf-8").decode("unicode-escape"))]

            base = 10
            if inst[1].startswith("0b"):
                base = 2
            elif inst[1].startswith("0x"):
                base = 16
            return [int(inst[1], base)]

        #check if possibly indirect, veery vibecoded
        ind = '(' in inst[1] and ')' in inst[1]
        inst[1] = inst[1].replace('(', "")
        inst[1] = inst[1].replace(')', "")

        #not a very robust way to check for rel addresses.
        if inst[0].upper() in ["BEQ", "BMI", "BNE", "BPL", "BVS", "BVC", "BCS", "BCC"]:
            #relative
            offset = int(inst[1][1:], 16) - pos - ORIGIN  # +2 because the instruction is 2 bytes long
            #print(f"Calculating relative offset for {inst[1]}: {int(inst[1][1:], 16)} - {pos} - {ORIGIN} = {offset}")
            return [INST_TABLE[inst_name]["rel"], offset]
        elif inst[1].startswith("#"):
            #immediate
            base = 10
            if inst[1][1:].startswith("0b"):
                base = 2
            elif inst[1][1:].startswith("0x"):
                base = 16
            return [INST_TABLE[inst_name]["imm"], int(inst[1][1:], base)]
        elif inst[1].startswith("$"):
            tp = "abs"

            #check for other modes
            if inst[1].endswith(",X"):
                tp = "absx"
                inst[1] = inst[1].split(",")[0]
            elif inst[1].endswith(",Y"):
                tp = "absy"
                inst[1] = inst[1].split(",")[0]
            elif ind:
                tp = "ind"

            #absolute
            base = 10
            if inst[1][1:].startswith("0b"):
                base = 2
            elif inst[1][1:].startswith("0x"):
                base = 16
            return [INST_TABLE[inst_name][tp], int(inst[1][1:], 16) & 0xFF, (int(inst[1][1:], 16) >> 8) & 0xFF]
        else:
            tp = "zp"

            if inst[1].endswith(",X"):
                if ind:
                    tp = "indx"
                else:
                    tp = "zpx"
                inst[1] = inst[1].split(",")[0]
            elif inst[1].endswith(",Y"):
                if ind:
                    tp = "indy"
                else:
                    tp = "zpy"
                inst[1] = inst[1].split(",")[0]

            base = 10
            if inst[1].startswith("0b"):
                base = 2
            elif inst[1].startswith("0x"):
                base = 16
            #zero page
            return [INST_TABLE[inst_name][tp], int(inst[1], 16)]
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
        "\t python zeusammen.py cmp [infile] -o [outfile]",

        "",
        "-o [outfile]: specify output file (default: a.bin)",
        "-S [strictness]: set strictness level (default: 1)",
        "\tStrictness levels:",
        "\t\t0: Very lenient, will allow potentially dangerous constructs with no warnings",
        "\t\t1: More strict, will warn about bad/unwanted practices", 
        "\t\t2: Very strict, will warn about any argument that is not a label, constant, or immediate vaThis is recommended if making/using libraries.",
        "-werr: Treat warnings as errors (implies -S 2)",
        "-to: Output the sanitized and symbolized program to test.to and exit (for testing",
        "-ld: Specify a library directory to search for .extern files (required if using .extern directives",
        "-dyns: Specify the starting address of the dynamic memory allocation pool (defaults to 0xFF00)",
        "-dyne: Specify the ending address of the dynamic memory allocation pool (defaults to 0xFFFF)",
        "",
        "Libraries are added to the TOP of the program, this makes parsing some things easier."
    )))
    
def sanitize(line: str) -> list[str]:
    global ORIGIN

    """
        Checks for invalid input and removes comments
        Breaks up lines into individual bytes

    Args:
        line (string): line of code to be sanitized
    """
    
    cmt_start: int = len(line)
    if ";" in line:
        cmt_start = line.index(";")
    if line.startswith(";") or line.strip() == "":
        return [""]

    if line.startswith(".org"):
        ORIGIN = int(line.split(" ")[1][1:], 16)
        return [""]
    if line.startswith(".extern"):
        return [""]
    
    #truncate without comment
    #split into bytes
    cde = line[:cmt_start]
    cde = cde.strip()
    if cde.startswith(".equ"):
        cde = [cde[:4], cde[4:].strip()]
    elif cde.startswith(".res"):
        cde = [cde[:4], cde[4:].strip()]
    else:
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
    
    global LABELS
    
    #pass 1
    #handle .equ definitions first, so we can use them in labels
    for i, inst in enumerate(prog):
        #equ syntax: .equ [name], [val]
        if inst[0].startswith(".equ"):
            parts = inst[1].split(",")
            if len(parts) != 2:
                print(f"Invalid .equ directive: {inst}")
                exit(1)
            sym_name = parts[0].strip()
            sym_value = parts[1].strip()
            if sym_name in CONSTANTS.keys():
                raise SymbolRedefinitionError(f"Constant {sym_name} is being redefined!")
            #check if sym_value is already somewhere
            for k in CONSTANTS.keys():
                ign = False
                if i-1 > 0:
                    ign = prog[i-1][0].strip() == ".ignore"
                if CONSTANTS[k] == sym_value and STRICTNESS > 0 and not ign:
                     if WARN_AS_ERRORS:
                          raise DoubleConstDefWarning(f"Constant {sym_value} is already defined as {k}!")
                     else:
                          warnings.warn(f"Constant {sym_name} is being defined with value {sym_value} which is already defined as {k}. This may lead to issues if {k} is a reserved address.", DoubleConstDefWarning)
            #check if maybe tries to go into dynamic memspace
            if sym_value.startswith("$") and int(sym_value[1:], 16) in range(DYN_MEM_START, DYN_MEM_END):
                if WARN_AS_ERRORS:
                    raise ConstInDynMemWarning(f"Constant {sym_name} is being defined in the dynamic memory pool.")
                else:
                    warnings.warn(f"Constant {sym_name} is being defined in the dynamic memory pool.", ConstInDynMemWarning)

            CONSTANTS[sym_name] = sym_value

        if inst[0].startswith(".res"):
            #.res syntax: .res [name], [size]
            #dynamically tries to reserve memory
            #with the given size
            parts = inst[1].split(",")
            if len(parts) != 2:
                print(f"Invalid .res directive: {inst}")
                exit(1)
            sym_name = parts[0].strip()
            sym_value = int(parts[1].strip())
            if sym_name in VARIABLES.keys() and not VARIABLES[sym_name]['released']:
                raise SymbolRedefinitionError(f"Variable {sym_name} is being redefined before being released!")
            #idk if we need to check if it already exists somewhere
            #run space finding algo
            m_ctr = 0
            for i in range(DYN_MEM_START, DYN_MEM_END+1):
                #inefficient
                for k in VARIABLES.keys():
                    if i in range(int(VARIABLES[k]['addr'][1:], 16), int(VARIABLES[k]['addr'][1:], 16)+VARIABLES[k]['size']) and not VARIABLES[k]['released']:
                        m_ctr = -1 #avoids having to do all sorts of shenanigans to continue parent loop
                        break

                m_ctr += 1
                if m_ctr == sym_value:
                    #found our free space
                    VARIABLES[sym_name] = {"addr": f"$0x{i-m_ctr+1:04X}", "size": sym_value, "released": False, "scope": None}
                    break
            else: #yes, i know, very weird
                raise OutOfMemoryError(f"Ran out of memory when trying to allocate memory of size {sym_value} for {sym_name}!")

        if inst[0].startswith(".rel"):
            #.rel syntax: .rel [name]
            #releases dynamically allocated memory
            inst[1] = inst[1].strip()
            if inst[1] not in VARIABLES.keys():
                raise VarUndefinedError(f"Undefined variable when trying to free {inst[1]}!")
            VARIABLES[inst[1]]['released'] = True


    byte_ctr: int = 0
    for i, inst in enumerate(prog):
        
        if inst[0].startswith(".equ"):
            continue #already handled .equ definitions
        if inst[0].startswith(".ignore"):
            continue
        if inst[0].startswith(".byte"):
            byte_ctr += 1
            continue
        if inst[0].startswith(".res"):
            continue
        if inst[0].startswith(".rel"):
            continue
        
        
        ign = False
        if i-1 > 0:
            ign = prog[i-1][0].strip() == ".ignore" 
        #check if previous is .ignore
        if STRICTNESS > 1 and not ign:
            #exit if an argument is NOT a label, constant, or immediate value
            for arg in inst[1:]:
                if arg.startswith("$"):
                    if WARN_AS_ERRORS:
                        raise DangerousArgWarning(f"Argument {arg} in instruction {i}:{inst[0]} is not a label, constant, or immediate value. This increases the risk of unexpected behavior.")
                    else:
                        warnings.warn(f"Argument {arg} in instruction {i}:{inst[0]} is not a label, constant, or immediate value. This increases the risk of unexpected behavior.", DangerousArgWarning)



        if inst[0].endswith(":"):
            #symbol definiton here
            if inst[0].strip(':') in LABELS.keys():
                raise SymbolRedefinitionError(f"Symbol {inst[0].strip(':')} is being redefined!")
            LABELS[inst[0].strip(":")] = "$" + str(hex(byte_ctr + ORIGIN))[2:].upper()
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
                #this essentially defeats the whole purpose of the 
                #big chunk of that replaces the vars with their vals

                ops = ["+", "-", "/", "*", "%"]

                name = inst[1]
                for op in ops:
                    name = name.split(op)[0]

                if name in CONSTANTS.keys():
                    if CONSTANTS[name].startswith("$"):
                        byte_ctr += 2
                    else:
                        byte_ctr += 1
                elif name in VARIABLES.keys():
                    byte_ctr += 2
                elif inst[1].startswith("$"):
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
        if prog[i][0].startswith(".equ"):
            prog.pop(i)
        if prog[i][0].startswith(".ignore"):
            prog.pop(i)
        if prog[i][0].startswith(".res"):
            prog.pop(i)
        if prog[i][0].startswith(".rel"):
            prog.pop(i)

    #remove any empty lines
    for i in range(len(prog)):
        if prog[i] == []:
            prog.pop(i)

    #check for start, more efficient this way than uppering or lowering
    if "start" not in LABELS.keys() and "START" not in LABELS.keys():
        raise StartUndefined("The program has no start!")

def preprocess(prog: list[list[str]]):
    global LABELS
    """
        Replaces things like variable names or labels with memory locations

    Args:
        prog (list[list[str]]): 
    """
    
    #now we replace
    for inst in prog:
        for i in range(len(inst)):
            #strip modifiers
            #this whole codeblock makes me nauseous.... 
            parts = inst[i].split(",")
            name = parts[0].strip("<").strip(">").strip("(").strip(")").strip()
            splitter = inst[i]
            splitter = splitter.split(parts[0].strip("(").strip(")"))

            #find the exact key that matches this var
            v_start = None
            v_end = None
            vidx = 0
            #labels
            for k in reversed(sorted(LABELS.keys(), key = lambda x : len(x))):
                for j, ch in enumerate(name):
                    if vidx >= len(k):
                        v_start = None
                        v_end = None
                        vidx = 0
                    if ch == k[vidx]:
                        if v_start == None:
                            v_start = j
                        vidx += 1
                    else:
                        v_start = None
                        v_end = None
                        vidx = 0
                    if vidx == len(k):
                        v_end = vidx
                        break
                if v_start is not None and v_end is not None:
                    #lets see if we want to split these values.
                    v_before = name[:v_start]
                    v_after  = name[v_end:]
                    v = name[v_start:v_end]

                    if LABELS[v].startswith("$"):
                        if inst[i].startswith("<"):
                            v = eval(f"{v_before}{int(LABELS[v][1:3],16)}{v_after}")
                            inst[i] = splitter[0] + '#0x' + f"{v:02X}" + splitter[1]
                            break
                        elif inst[i].startswith(">"):
                            v = eval(f"{v_before}{int(LABELS[v][1:3],16)}{v_after}")
                            inst[i] = splitter[0] + '#0x' + f"{v:02X}" + splitter[1]
                            break 
                    v = eval(f"{v_before}{int(LABELS[v][1:],16)}{v_after}")
                    inst[i] = splitter[0] + f"$0x{v:04X}" + splitter[1]
                    break

            if v_start is None and v_end is None:
                vidx = 0
                for k in reversed(sorted(CONSTANTS.keys(), key = lambda x : len(x))):
                    for j, ch in enumerate(name):
                        if vidx >= len(k):
                            v_start = None
                            v_end = None
                            vidx = 0
                        if ch == k[vidx]:
                            if v_start == None:
                                v_start = j
                            vidx += 1
                        else:
                            v_start = None
                            v_end = None
                            vidx = 0
                        if vidx == len(k):
                            v_end = vidx
                            break
                    if v_start is not None and v_end is not None:
                        #lets see if we want to split these values.
                        v_before = name[:v_start]
                        v_after  = name[v_end:]
                        v = name[v_start:v_end]

                        if CONSTANTS[v].startswith("$"):
                            if inst[i].startswith("<"):
                                v = eval(f"{v_before}{int(CONSTANTS[v][1:5],16)}{v_after}")
                                inst[i] = splitter[0] + '#0x' + f"{v:02X}" + splitter[1]
                                break
                            elif inst[i].startswith(">"):
                                v = eval(f"{v_before}{int(CONSTANTS[v][5:8],16)}{v_after}")
                                inst[i] = splitter[0] + '#0x' + f"{v:02X}" + splitter[1]
                                break

                            v = eval(f"{v_before}{int(CONSTANTS[v][1:],16)}{v_after}")
                            inst[i] = splitter[0] + f"$0x{v:04X}" + splitter[1]
                            break
                        if CONSTANTS[v].startswith("#"):
                            v = eval(f"{v_before}{int(CONSTANTS[v][1:],16)}{v_after}")
                            inst[i] = splitter[0] + f"#0x{v:02X}" + splitter[1]
                            break
                        v = eval(f"{v_before}{int(CONSTANTS[v],16)}{v_after}")
                        inst[i] = splitter[0] + f"0x{v:02X}" + splitter[1]

            if v_start is None and v_end is None:
                vidx = 0
                for k in reversed(sorted(VARIABLES.keys(), key = lambda x : len(x))):
                    for j, ch in enumerate(name):
                        if vidx >= len(k):
                            v_start = None
                            v_end = None
                            vidx = 0
                        if ch == k[vidx]:
                            if v_start == None:
                                v_start = j
                            vidx += 1
                        else:
                            v_start = None
                            v_end = None
                            vidx = 0
                        if vidx == len(k):
                            v_end = vidx
                            break
                    if v_start is not None and v_end is not None:
                        #lets see if we want to split these values.
                        v_before = name[:v_start]
                        v_after  = name[v_end:]
                        v = name[v_start:v_end]

                        if VARIABLES[v]['released']:
                            raise WriteAfterRelease(f"Trying to write into released variable {name}!")


                        if inst[i].startswith("<"):
                            v = eval(f"{v_before}{int(VARIABLES[v]['addr'][1:5],16)}{v_after}")
                            inst[i] = splitter[0] + '#0x' + f"{v:02X}" + splitter[1]
                            break
                        elif inst[i].startswith(">"):
                            v = eval(f"{v_before}{int(VARIABLES[v]['addr'][5:8],16)}{v_after}")
                            inst[i] = splitter[0] + '#0x' + f"{v:02X}" + splitter[1]
                            break

                        v = eval(f"{v_before}{int(VARIABLES[v]['addr'][1:],16)}{v_after}")
                        inst[i] = splitter[0] + f"$0x{v:04X}" + splitter[1]
                        break

    #can be done after TEST_OUTPUT a little faster
    #but i want this check to be performed on test
    #outputs too
    for inst in prog:
        #check for valid param
        if len(inst) == 1:
            continue
        try:
            #skips possible prefixes
            #can maybe cause isues undef vars
            #with name length one?
            if inst[1].startswith("("):
                #just pass for now but this is a TODO
                continue
            if inst[1].startswith("#") or inst[1].startswith("$"):
                int(inst[1][1:], 0) #autobase
        except ValueError:
            print(inst)
            raise VarUndefinedError(f"{inst[1]} is undefined!")

    if TEST_OUTPUT:
        byte_ctr = 0
        with open("test.to", "w+") as f:
            for eline in prog:
                f.write((str(hex(byte_ctr + ORIGIN))) + ": " + ' '.join(eline) + '\n')
                byte_ctr += 1
                if len(eline) == 1:
                    continue

                #check for branch instructions
                if eline[1].startswith("$") and not eline[0] in ["BCC", "BCS", "BNE", "BPL", "BMI", "BPL", "BVC", "BVS"]:
                    byte_ctr += 2
                else:
                    byte_ctr += 1
        print(f"Dumped debug output to test.to")
        exit(0)
   
    #convert instructions to bytes
    byte_cnter = 0
    for i in range(len(prog)):
        #handle possible absolute args for byte_cnter
        if len(prog[i]) > 1:
            if prog[i][1].startswith("$") and prog[i][0].upper() not in ["BCC", "BCS", "BNE", "BPL", "BMI", "BPL", "BVC", "BVS"]:
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
                f.write(int(LABELS['START'][1:], 16).to_bytes(num_bytes, "little"))
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
    global LABELS
    global ORIGIN   
    """
        Essentially a function that gathers all the steps in the compilation process

    Args:
        infile (str): input file
        outfile (str): output file
    """
    
    main: list = []
    with open(infile, "r") as f:
        for line in f:
            line = line.strip()
            if any((line.strip() == "",
                   line.startswith(";"),
                   line.startswith("\n"))):
                continue

            san = sanitize(line)
            if san != [""]:
                main.append(san)

    sanitized = []

    recurse_libs(infile, lib_dir)
    import_libs(sanitized, lib_dir)
 
    sanitized.extend(main)

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
    for i in range(2, len(args)):
        match args[i]:
            case "-to":
                TEST_OUTPUT = True
            case "-o": 
                if i + 1 >= len(args):
                    print("Please supply an output file after -o")
                    exit(1)
                OUTPUT_FILE = args[i + 1]
            case "-S":
                if i + 1 >= len(args):
                    print("Please supply a value after -S")
                    exit(1)
                STRICTNESS = int(args[i + 1])
            case "-ld":
                if i + 1 >= len(args):
                    print("Please supply a library directory after -ld")
                    exit(1)
                LIB_DIR = args[i + 1]
            case "-dyns":
                if i + 1 >= len(args):
                    print("Please supply a memory address after -dyns")
                    exit(1)
                DYN_MEM_START = int(args[i + 1], 16)
            case "-dyne":
                if i + 1 >= len(args):
                    print("Please supply a memory address after -dyne")
                    exit(1)
                DYN_MEM_END = int(args[i + 1], 16)
            case "-werr":
                WARN_AS_ERRORS = True
            case "-df":
                DUMP_DF = True


    rn_cmp(args[1], OUTPUT_FILE, LIB_DIR)

    for k in LABELS.keys():
        print(f"{k}: {LABELS[k]}")

    if DUMP_DF:
        #dump debug flags, maybe use json??
        with open(OUTPUT_FILE + ".df", "w+") as f:
            f.write(".begin CONSTANTS\n")
            for k in CONSTANTS.keys():
                f.write(f"{CONSTANTS[k]}-{k}\n")
            f.write(".begin VARIABLES\n")
            for k in VARIABLES.keys():
                f.write(f"{VARIABLES[k]['addr']}:")
                f.write(','.join((
                    f"name-{k}",
                    f"size-{VARIABLES[k]['size']}",
                    f"scope-{VARIABLES[k]['scope']}\n",
                    )))
            f.write(".begin LABELS\n")
            for k in LABELS.keys():
                f.write(f"{LABELS[k]}-{k}\n")

from enum import Enum
import sys
import serial
import time
from tqdm import tqdm

class SlaveShadow():
    _WRITE_ADDRESS = 0x10
    _READ_ADDRESS = 0x11
    _WRITE_STREAM = 0x12

    @staticmethod
    def write(sobj, address, data):
        addr_high = (address >> 8) & 0xFF
        addr_low = address & 0xFF
        sobj.write(bytearray((SlaveShadow._WRITE_ADDRESS, addr_high, addr_low, data)))
        #wait for ack
        sobj.read(1)
    @staticmethod
    def read(sobj, address):
        addr_high = (address >> 8) & 0xFF
        addr_low = address & 0xFF
        sobj.write(bytearray((SlaveShadow._READ_ADDRESS, addr_high, addr_low, 0)))
        return sobj.read(1)[0]
    @staticmethod
    def stream_write(sobj, start_address, data_block):
        size = len(data_block)
        addr_high = (start_address >> 8) & 0xFF
        addr_low = start_address & 0xFF
        
        header = bytearray([SlaveShadow._WRITE_STREAM, addr_high, addr_low, size])
        sobj.write(header)
        
        sobj.write(bytearray(data_block))
        
        while not (val := sobj.read(1)): pass

class WorkMode(Enum):
    WRITE = 0
    STREAM_WRITE = 1
    READ = 2
    CLEAR = 3
    READ_ADDRESS = 4

class SpeedMode(Enum):
    NORMAL = 0
    FAST = 1

MODE = None
SPEED = SpeedMode.NORMAL
FILE = None
ADDRESS = None
PORT = None
RANGE = None
SKIP_NULLB = False

def parse_args():
    global MODE, SPEED, FILE, PORT, ADDRESS, RANGE, SKIP_NULLB

    i = 0
    argv = sys.argv[1:]
    while i < len(argv):
        arg = argv[i]
        match arg:
            case '-w':
                MODE = WorkMode.WRITE
                i+=1
                if i < len(argv):
                    FILE = argv[i]
            case '-sw':
                MODE = WorkMode.STREAM_WRITE
                i+=1
                if i < len(argv):
                    FILE = argv[i]
            case '-r':
                MODE = WorkMode.READ
                i+=1
                if i < len(argv):
                    FILE = argv[i]
            case '-F':
                SPEED = SpeedMode.FAST
            case '-p':
                i+=1
                if i < len(argv):
                    PORT = argv[i]
            case '-s0':
                SKIP_NULLB = True
            case '--clear':
                MODE = WorkMode.CLEAR
            case '-ar':
                i+=1
                if i < len(argv):
                    RANGE = [int(x) for x in argv[i].split(',')]
            case '-rA':
                MODE = WorkMode.READ_ADDRESS
                i+=1
                if i < len(argv):
                    ADDRESS = int(argv[i])

            case _:
                print(f"Invalid argument {arg}") 
                exit(1)
        i+=1 

    #check args
    if MODE != WorkMode.READ_ADDRESS:
        ADDRESS =-1

    if any((
            MODE == None,
            PORT == None,
            ADDRESS == None,
            )):
        print("Not all arguments specified")
        exit(1)
    if FILE == None:
        if MODE == WorkMode.WRITE:
            FILE = sys.stdin.buffer
        if MODE == WorkMode.READ:
            FILE = sys.stdout.buffer
    else:
        FILE = open(FILE, "wb") if MODE == WorkMode.READ else open(FILE, "rb")

    if RANGE == None:
        RANGE = [0, 32768]


if __name__ == "__main__":
    parse_args()

    ser = serial.Serial(PORT, 115200)
    #wait some time for arduino to boot
    time.sleep(3)
    ser.reset_input_buffer()

    match MODE:
        case WorkMode.READ_ADDRESS:
            #read a specific address and print it out
            val = SlaveShadow.read(ser, ADDRESS)
            print(val)
        case WorkMode.READ:
            for i in range(RANGE[0], RANGE[1]):
                FILE.write(SlaveShadow.read(ser, i).to_bytes())
        case WorkMode.WRITE:
            data = FILE.read(32_768)
            for i, byte in tqdm(enumerate(data), total=len(data), unit='bytes'):
                if SKIP_NULLB and byte == 0:
                    continue
                SlaveShadow.write(ser, i, byte)
            
            match SPEED:
                case SpeedMode.NORMAL:
                    print("Veryfing")
                    ser.setDTR(False)
                    time.sleep(0.1)
                    ser.setDTR(True)
                    time.sleep(3)
                    ser.reset_input_buffer()
                    #verify file
                    for i, byte in tqdm(enumerate(data), total=len(data), unit='bytes'):
                        red = SlaveShadow.read(ser, i)
                        if byte != red:
                            print("Upload corrupted!")
                            exit(1)
                case _:
                    pass
        case WorkMode.STREAM_WRITE:
            data = FILE.read(32768)
            chunk_size = 64
            
            with tqdm(total=len(data), unit='B', unit_scale=True) as pbar:
                for i in range(0, len(data), chunk_size):
                    chunk = data[i : i + chunk_size]
                    SlaveShadow.stream_write(ser, i, chunk)
                    pbar.update(len(chunk))
            match SPEED:
                case SpeedMode.NORMAL:
                    print("Veryfing")
                    ser.setDTR(False)
                    time.sleep(0.1)
                    ser.setDTR(True)
                    time.sleep(3)
                    ser.reset_input_buffer()
                    #verify file
                    for i, byte in tqdm(enumerate(data), total=len(data), unit='bytes'):
                        red = SlaveShadow.read(ser, i)
                        if byte != red:
                            print("Upload corrupted!")
                            exit(1)
                case _:
                    pass

            
        case WorkMode.CLEAR:
            for _, i in tqdm(enumerate(range(RANGE[0], RANGE[1])), total=len(range(RANGE[0], RANGE[1])), unit='bytes'):
                SlaveShadow.write(ser, i, 0)
            match SPEED:
                case SpeedMode.NORMAL:
                    print("Veryfing")
                    ser.setDTR(False)
                    time.sleep(0.1)
                    ser.setDTR(True)
                    time.sleep(3)
                    ser.reset_input_buffer()
                    #verify file
                    for _, i in tqdm(enumerate(range(RANGE[0], RANGE[1])), total=len(range(RANGE[0], RANGE[1])), unit='bytes'):
                        red = SlaveShadow.read(ser, i)
                        if red != 0:
                            print("Upload corrupted!")
                            exit(1)
                case _:
                    pass   

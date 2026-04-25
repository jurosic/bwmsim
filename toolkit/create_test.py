from sys import argv

PATTERN = None
OUTPUT = None
SIZE = None

def parse_args():
    global PATTERN, OUTPUT, SIZE

    i = 0
    while i < len(argv):
        match argv[i]:
            case "-s":
                i += 1
                SIZE = int(argv[i])
            case "-o":
                i += 1
                OUTPUT = argv[i]
            case "-p":
                i += 1
                PATTERN = [x for x in argv[i].split(",")]
        i+=1
if __name__ == "__main__":
    parse_args()

    with open(OUTPUT, "wb") as f:
        for _ in range(0, int(SIZE/len(PATTERN))):
            for pat in PATTERN:
                f.write(int(pat, 16).to_bytes())

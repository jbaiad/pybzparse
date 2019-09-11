import sys

import bitstring


def parse(filepath):
    bstr = bitstring.ConstBitStream(filename=filepath)

    while bstr.pos < bstr.len:
        box_size, box_type = bstr.readlist("uint:32, bytes:4")
        box_size -= 8

        try:
            box_type = box_type.decode("utf-8")
        except UnicodeDecodeError:
            pass

        if box_size == 1:
            print("Using big size")
            box_size = bstr.read("uint:64")
            box_size -= 8

        print(box_type)
        bstr.read(box_size * 8)

if __name__ == "__main__":
    print(f"Executing with filepath arg {sys.argv[1]}")
    parse(sys.argv[1])

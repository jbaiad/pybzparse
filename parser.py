import sys

import bitstring


def parse(filepath):
    bstr = bitstring.ConstBitStream(filename=filepath)

    while bstr.pos < bstr.len:
        box_size, box_type = bstr.readlist("uint:32, bytes:4")

        try:
            box_type = box_type.decode("utf-8").upper()
        except UnicodeDecodeError:
            pass

        if box_size == 1:
            print("Using big size")
            box_size = bstr.read("uint:64")
            box_size -= 8

        box_size -= 8
        print(box_type)
        bstr.read(box_size * 8)


class BoxParser:
    def __init__(self, box_size, box_type):
        self._start_pos = None
        self._bytes_read = 0
        self.box_type = box_type
        self.box_size = box_size
        self.uuid = None

    def parse(self, bstr: bitstring.ConstBitStream):
        self._start_pos = bstr.pos
        if self.box_size == 1:
            self.box_size = bstr.read("uint:64")
        elif self.box_size == 0:
            self.box_size = bstr.len - bstr.pos

        if self.box_type.upper() == "UUID":
            self.uuid = bstr.read("bytes:16")


class FullBox(Box):
    def parse(self, bstr: bitstring.ConstBitStream):
        super().parse(bstr)
        i


if __name__ == "__main__":
    print(f"Executing with filepath arg {sys.argv[1]}")
    parse(sys.argv[1])

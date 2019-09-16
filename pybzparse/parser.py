import pprint
import sys

import bitstring

from pybzparse import boxes


class Parser:
    def __init__(self, filepath: str):
        self.filepath: str = filepath
        self.bstr: bitstring.ConstBitStream = bitstring.ConstBitStream(filename=filepath)
        self.current_box: boxes.Box = self.get_next_box()

    def __repr__(self):
        return pprint.pformat(self.__dict__)

    def __iter__(self):
        while self.bstr.pos < self.bstr.len:
            yield self.current_box
            self.current_box = self.get_next_box()

    def get_next_box(self):
        start_pos = self.bstr.pos
        size, code = self.bstr.readlist("uint:32, bytes:4")

        if size == 1:
            size = self.bstr.read("uint:64")
        elif size == 0:
            size = self.bstr.len - start_pos

        try:
            code = code.decode("utf-8").upper()
        except UnicodeDecodeError:
            pass

        if code.upper() == "UUID":
            usertype = self.bstr.read("bytes:16")
        else:
            usertype = None

        if not hasattr(boxes, code):
            print(f"Encountered unknown box code: {code}")
            constructor = boxes.Box
            self.bstr.read(size * 8 - (self.bstr.pos - start_pos))
        else:
            constructor = getattr(boxes, code)

        return constructor(self.bstr, start_pos, size * 8, usertype)


if __name__ == "__main__":
    for box in Parser('/Users/jbaiad/Downloads/(autoP - mp4) Neon+Genesis+Evangelion++Episode+10.mp4'):
        print(box.__repr__())


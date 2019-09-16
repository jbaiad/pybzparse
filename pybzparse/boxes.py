import datetime
import pprint
from typing import Optional

import bitstring

import pybzparse.descriptors as descriptors


TIME_OFFSET = datetime.datetime(1904, 1, 1)


def fixed_point_num(n_left_digits, n_right_digits):
    num = 0

    for i, bit in enumerate(n_left_digits[::-1]):
        num += bit * 2**i

    for i, bit in enumerate(n_right_digits):
        num += bit * 2**(-i - 1)

    return num


class Box:
    def __init__(self, bstr: bitstring.ConstBitStream , start_pos: int, size: int, usertype: Optional[bytes]):
        self.bstr = bstr
        self.start_pos = start_pos
        self.size = size
        self.usertype = usertype

    def __repr__(self):
        attributes = "\n  ".join([
            f"{k}={repr(v)}" for k, v in self.__dict__.items()
        ])
        return f"{self.__class__.__name__}(\n  {attributes}\n)\n"

    def get_num_remaining_bits(self):
        return self.start_pos + self.size - self.bstr.pos


class FullBox(Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = self.bstr.read("uint:8")
        self.flags = self.bstr.read("bits:24")


class FTYP(Box):
    """
    File Type Box
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.major_brand = self.bstr.read("bytes:4")
        self.minor_version = self.bstr.read("uint:32")
        self.compatible_brands = []
        while self.bstr.pos < self.start_pos + self.size:
            self.compatible_brands.append(self.bstr.read("bytes:4"))

        assert self.bstr.pos == self.start_pos + self.size


class MOOV(Box):
    """
    Movie Box
    """
    pass


class MVHD(FullBox):
    """
    Movie Header Box
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.version == 1:
            self.creation_time = self.bstr.read("uint:64")
            self.modification_time = self.bstr.read("uint:64")
            self.timescale = self.bstr.read("uint:32")
            self.duration = self.bstr.read("uint:64")
        elif self.version == 0:
            self.creation_time = self.bstr.read("uint:32")
            self.modification_time = self.bstr.read("uint:32")
            self.timescale = self.bstr.read("uint:32")
            self.duration = self.bstr.read("uint:32")
        else:
            raise ValueError

        self.creation_time = TIME_OFFSET + datetime.timedelta(seconds=self.creation_time)
        self.modification_time = TIME_OFFSET + datetime.timedelta(seconds=self.modification_time)

        self.rate = fixed_point_num(self.bstr.read("bits:16"), self.bstr.read("bits:16"))
        self.volume = fixed_point_num(self.bstr.read("bits:8"), self.bstr.read("bits:8"))
        
        # Skip reserved bits
        self.bstr.read("bits:16")
        self.bstr.readlist(["uint:32"] * 2)

        self.matrix = self.bstr.readlist(["int:32"] * 9)

        # Skip predefined bits
        self.bstr.readlist(["bits:32"] * 6)

        self.next_track_id = self.bstr.read("uint:32")


class IODS(FullBox):
    """
    Object Descriptor Box
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object_descriptor = descriptors.InitialObjectDescriptor(self.bstr)


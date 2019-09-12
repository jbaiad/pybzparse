import abc

import bitstring


class AbstractBoxMeta(abc.ABCMeta):
    def __init__(cls, name, base_classes, attrs):
        assert "type_code" in attrs or name.startswith("Abstract")
        super().__init__(name, base_classes, attrs)


class AbstractBox(metaclass=AbstractBoxMeta):
    def _parse_header(self, bit_str: bitstring.ConstBitStream):
        box_size, box_type = bit_str.readlist("uint:32, bytes:4")
        try:
            box_type = box_type.decode("utf-8")
        except UnicodeDecodeError:
            pass

        if box_size == 1:
            box_size = bit_str.read("uint:64")

        return box_size, box_type


    @abc.abstractmethod
    def parse(self, bit_str, box_size):
        """
        Parse a bit string corresponding with a type corresponding to the class's type_code attribute.

        bit_str: bitstring.ConstantBitStream pointing to the beginning (i.e., the header) of this box
        """
        pass

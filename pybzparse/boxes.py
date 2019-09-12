import pybzparse.utils as utils


class UnknownBox(utils.AbstractBox):
    type_code = "UNKNOWN"

    def parse(self, bit_str, box_size):
        print(f"skipping {box_size} bytes")
        bit_str.read(box_size * 8)


class FileTypeBox(utils.AbstractBox):
    type_code = "ftyp"

    def __init__(self):
        self.compatible_brands = []

    def parse(self, bit_str, box_size):
        # After this has run, we're guaranteed that self.compatible_brands is nonempty
        while box_size > 0:
            brand = bit_str.read("bytes:4")
            try:
                brand = brand.decode("utf-8")
            except UnicodeDecodeError:
                pass

            self.compatible_brands.append(brand)
            box_size -= 4

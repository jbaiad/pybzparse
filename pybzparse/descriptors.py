import enum

import bitstring


class DescriptorTag(enum.Enum):
    MIN_FORBIDDEN = 0
    OBJECT_DESCR = 1
    INITIAL_OBJECT_DESCR = 2
    ES_DESCR = 3
    DECODER_CONFIG_DESCR = 4
    DEC_SPECIFIC_INFO = 5
    SL_CONFIG_DESCR = 6
    CONTENT_IDENT_DESCR = 7
    SUPPL_CONTENT_IDENT_DESCR = 8
    IPI_DESCR_POINTER = 9
    IPMP_DESCR_POINTER = 10
    IPMP_DESCR = 11
    QOS_DESCR = 12
    REGISTRATION_DESCR = 13
    ES_ID_INC = 14
    ES_ID_REF = 15
    MP4_IOD = 16
    MP4_OD = 17
    IPL_DESCR_POINTER_REF = 18
    EXTENSION_PROFILE_LEVEL_DESCR = 19
    PROFILE_LEVEL_INDICATION_INDEX_DESCR = 20
    CONTENT_CLASSIFICATION_DESCR = 64
    RATING_DESCR = 65
    KEYWORD_DESCR = 66
    LANGUAGE_DESCR = 67
    SHORT_TEXTUAL_DESCR = 68
    EXPANDED_TEXTUAL_DESCR = 69
    CONTENT_CREATOR_NAME_DESC = 70
    CONTENT_CREATION_DATE_DESCR = 71
    OCI_CREATOR_NAME_DESCR = 72
    OCI_CREATION_DATE_DESCR = 73
    SMPTE_CAMERA_POSITION_DESCR = 74
    SEGMENT_DESCR = 75
    MEDIA_TIME_DESCR = 76
    MAX_FORBIDDEN = 255




class BaseDescriptor:
    def __init__(self, bstr: bitstring.ConstBitStream):
        self.tag = DescriptorTag(bstr.read("uint:8"))
        assert self.tag != DescriptorTag.MIN_FORBIDDEN and self.tag != DescriptorTag.MAX_FORBIDDEN

    def __repr__(self):
        attributes = "\n  ".join([
            f"{k}={repr(v)}" for k,v in self.__dict__.items()
        ])
        return f"{self.__class__.__name__}(\n  {attributes}\n)\n"


class ObjectDescriptorBase(BaseDescriptor):
    def __init__(self, bstr: bitstring.ConstBitStream):
        super().__init__(bstr)
        assert self.tag in {
            DescriptorTag.OBJECT_DESCR, DescriptorTag.MP4_OD,
            DescriptorTag.INITIAL_OBJECT_DESCR, DescriptorTag.MP4_IOD
        }



class ObjectDescriptor(ObjectDescriptorBase):
    def __init__(self, bstr: bitstring.ConstBitStream):
        super().__init__(bstr)
        assert self.tag == DescriptorTag.OBJECT_DESCR or self.tag == DescriptorTag.MP4_OD

        self.id = bstr.read("bits:10")
        self.url_flag = bstr.read("bits:1")
        
        # Skip reserved section
        bstr.read("bits:5")

        if self.url_flag:
            self.url_length = bstr.read("bits:8")
            self.url_string = bstr.read(f"bytes:{self.url_length}")
        else:
            self.es_descriptors = ElementaryStreamDescriptor(bstr) 


class InitialObjectDescriptor(ObjectDescriptorBase):
    def __init__(self, bstr:bitstring.ConstBitStream):
        super().__init__(bstr)
        assert self.tag == DescriptorTag.INITIAL_OBJECT_DESCR or self.tag == DescriptorTag.MP4_IOD

        self.id = bstr.read("bits:10")
        assert self.id != 0 and self.id != 1023

        self.url_flag = bstr.read("bits:1")
        self.include_inline_profile_level_flag = bstr.read("bits:1")

        # Skip reserved section
        reserved = bstr.read("bits:4")

        if self.url_flag:
            self.url_length = bstr.read("bits:8")
            self.url_string = bstr.read(f"bytes:{self.url_length}")
        else:
            self.od_profile_level_indication = bstr.read("bits:8")
            self.scene_profile_level_indication = bstr.read("bits:8")
            self.audio_profile_level_indication = bstr.read("bits:8")
            self.visual_profile_level_indication = bstr.read("bits:8")
            self.graphics_profile_level_indication = bstr.read("bits:8")
            self.es_descriptors = []
            self.oci_descriptors = []
            self.ipmp_descriptor_pointers = []
            self.ipmp_descriptors = []
            self.ipmp_tool_list_descriptors = []

            while DescriptorTag(bstr.peek("uint:8")) == DescriptorTag.ES_DESCR:
                self.es_descriptors.append(ElementaryStreamDescriptor(bstr))
            
            assert self.es_descriptors

        import ipdb; ipdb.set_trace()


class ElementaryStreamDescriptor(BaseDescriptor):
    def __init__(self, bstr: bitstring.ConstBitStream):
        super().__init__(bstr)
        assert self.tag == DescriptorTag.ES_DESCR

        self.id = bstr.read("bits:16")
        self.stream_dependence_flag = bstr.read("bits:1")
        self.url_flag = bstr.read("bits:1")
        self.ocr_stream_flag = bstr.read("bits:1")
        self.stream_priority = bstr.read("bits:5")

        if self.stream_dependence_flag:
            self.depends_on_es_id = bstr.read("bits:16")

        if self.url_flag:
            self.url_length = bstr.read("bits:8")
            self.url_string = bstr.read(f"bytes:{self.url_length}")

        if self.ocr_stream_flag:
            self.ocr_es_id = bstr.read("bits:16")

        self.decoder_config_descriptor = DecoderConfigDescriptor(bstr)

        import ipdb; ipdb.set_trace()


class DecoderConfigDescriptor(BaseDescriptor):
    def __init__(self, bstr: bitstring.ConstBitStream):
        super().__init__(bstr)
        self.object_type_indication = bstr.read("bits:8")
        self.stream_type = bstr.read("bits:6")
        self.upstream = bstr.read("bits:1")
        
        # Skip reserved section
        bstr.read("bits:1")

        self.buffer_size_db = bstr.read("bits:24")
        self.max_bitrate = bstr.read("bits:32")
        self.avg_bitrate = bstr.read("bits:32")



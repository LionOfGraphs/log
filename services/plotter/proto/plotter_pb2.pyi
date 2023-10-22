from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PlotRequest(_message.Message):
    __slots__ = ["rawData", "encodedPayload"]
    RAWDATA_FIELD_NUMBER: _ClassVar[int]
    ENCODEDPAYLOAD_FIELD_NUMBER: _ClassVar[int]
    rawData: bytes
    encodedPayload: bytes
    def __init__(self, rawData: _Optional[bytes] = ..., encodedPayload: _Optional[bytes] = ...) -> None: ...

class PlotResponse(_message.Message):
    __slots__ = ["image"]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    image: bytes
    def __init__(self, image: _Optional[bytes] = ...) -> None: ...

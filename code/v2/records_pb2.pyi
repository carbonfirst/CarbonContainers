from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class LookupReply(_message.Message):
    __slots__ = ["results"]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: str
    def __init__(self, results: _Optional[str] = ...) -> None: ...

class LookupRequest(_message.Message):
    __slots__ = ["name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class UpdateReply(_message.Message):
    __slots__ = ["code"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: str
    def __init__(self, code: _Optional[str] = ...) -> None: ...

class UpdateRequest(_message.Message):
    __slots__ = ["name", "setts", "value"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SETTS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    setts: str
    value: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ..., setts: _Optional[str] = ...) -> None: ...

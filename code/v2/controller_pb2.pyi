from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class MigrateReply(_message.Message):
    __slots__ = ["code"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: str
    def __init__(self, code: _Optional[str] = ...) -> None: ...

class MigrateRequest(_message.Message):
    __slots__ = ["conts"]
    CONTS_FIELD_NUMBER: _ClassVar[int]
    conts: str
    def __init__(self, conts: _Optional[str] = ...) -> None: ...

class RecieveReply(_message.Message):
    __slots__ = ["code"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: str
    def __init__(self, code: _Optional[str] = ...) -> None: ...

class RecieveRequest(_message.Message):
    __slots__ = ["cont"]
    CONT_FIELD_NUMBER: _ClassVar[int]
    cont: str
    def __init__(self, cont: _Optional[str] = ...) -> None: ...

import sys
import os

from typing import Text, Union, Any, MutableMapping, MutableSequence, Optional, Tuple

_pathlike = Union[Text, bytes, 'os.PathLike[Any]']
_uri = Union[Text, str]

if sys.version_info[0] == 2:
    if sys.platform == "win32":
        _base = Text
    else:
        _base = bytes
else:
    _base = Text

class fsnative(_base):
    def __init__(self, object: Text=u"") -> None:
        ...

def path2fsn(path: _pathlike) -> fsnative:
    ...

def fsn2text(path: fsnative, strict: bool=False) -> Text:
    ...

def text2fsn(text: Text) -> fsnative:
    ...

def fsn2bytes(path: fsnative, encoding: str="utf-8") -> bytes:
    ...

def bytes2fsn(data: bytes, encoding: str="utf-8") -> fsnative:
    ...

def uri2fsn(uri: _uri) -> fsnative:
    ...

def fsn2uri(path: fsnative) -> Text:
    ...

def fsn2norm(path: fsnative) -> fsnative:
    ...

sep: fsnative
pathsep: fsnative
curdir: fsnative
pardir: fsnative
altsep: fsnative
extsep: fsnative
devnull: fsnative
defpath: fsnative

def getcwd() -> fsnative:
    ...

def getenv(key: _pathlike, value: Optional[fsnative]=None) -> Optional[fsnative]:
    ...

def putenv(key: _pathlike, value: _pathlike):
    ...

def unsetenv(key: _pathlike) -> None:
    ...

def supports_ansi_escape_codes(fd: int) -> bool:
    ...

def expandvars(path: _pathlike) -> fsnative:
    ...

def expanduser(path: _pathlike) -> fsnative:
    ...

environ: MutableMapping[fsnative,fsnative]
argv: MutableSequence[fsnative]

def gettempdir() -> fsnative:
    pass

def mkstemp(suffix: Optional[_pathlike]=None, prefix: Optional[_pathlike]=None, dir: Optional[_pathlike]=None, text: bool=False) -> Tuple[int, fsnative]:
    ...

def mkdtemp(suffix: Optional[_pathlike]=None, prefix: Optional[_pathlike]=None, dir: Optional[_pathlike]=None) -> fsnative:
    ...

version_string: str

version: Tuple[int, int, int]

print_ = print

def input_(prompt: Any=None) -> fsnative:
    ...

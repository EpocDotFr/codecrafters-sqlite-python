from typing import Optional
import enum


@enum.unique
class WriteVersion(enum.IntEnum):
    Legacy = 1
    Wal = 2


@enum.unique
class ReadVersion(enum.IntEnum):
    Legacy = 1
    Wal = 2


@enum.unique
class DatabaseTextEncoding(enum.IntEnum):
    Utf8 = 1
    Utf16Le = 2
    Utf16Be = 3

    def python(self) -> Optional[str]:
        if self == self.Utf8:
            return 'utf-8'
        elif self == self.Utf16Le:
            return 'utf-16-le'
        elif self == self.Utf16Be:
            return 'utf-16-be'

        return None


@enum.unique
class PageType(enum.IntEnum):
    InteriorIndex = 2
    InteriorTable = 5
    LeafIndex = 10
    LeafTable = 13

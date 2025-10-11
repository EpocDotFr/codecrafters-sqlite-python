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


@enum.unique
class PageType(enum.IntEnum):
    InteriorIndex = 2
    InteriorTable = 5
    LeafIndex = 10
    LeafTable = 13

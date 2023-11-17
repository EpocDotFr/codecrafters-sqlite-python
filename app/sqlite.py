from typing import BinaryIO, Any
import struct
import os


class SQLiteFile:
    f: BinaryIO
    page_size: int

    def __init__(self, f: BinaryIO):
        self.f = f

        if self.read_bytes(16) != b'SQLite format 3\x00':
            raise ValueError('Not a SQLite file')

        self.page_size = self.read_uint16()

    @classmethod
    def exec(cls, f: BinaryIO, command: str) -> str:
        sqlite = cls(f)

        if command[0] == '.': # Dot command
            if command == '.dbinfo':
                return sqlite.exec_dbinfo()
            elif command == '.tables':
                raise NotImplementedError()
            else:
                raise ValueError('Unknown dot command')
        else: # SQL query
            raise NotImplementedError()

    def exec_dbinfo(self) -> str:
        return '\n'.join((
            f'database page size: {self.page_size}',
            f'number of tables: TODO'
        ))

    def unpack(self, fmt: str, size: int = 1) -> Any:
        ret = struct.unpack(
            f'>{fmt}',
            self.read_bytes(size)
        )

        return ret[0] if len(ret) == 1 else ret

    def read_uint16(self) -> int:
        return self.unpack('H', 2)

    def read_bytes(self, size: int) -> bytes:
        return self.f.read(size)

    def read_byte(self) -> bytes:
        return self.read_bytes(1)

    def move(self, offset: int) -> None:
        self.f.seek(offset, os.SEEK_CUR)

    def move_set(self, offset: int) -> None:
        self.f.seek(offset, os.SEEK_SET)

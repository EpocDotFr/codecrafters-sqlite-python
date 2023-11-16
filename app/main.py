from typing import BinaryIO
import argparse
import struct
import os


class SQLiteFile:
    f: BinaryIO

    def __init__(self, f: BinaryIO):
        self.f = f

    def exec(self, command: str) -> None:
        if command[0] == '.': # Dot command
            if command == '.dbinfo':
                self.move(16)

                print(f'database page size: {self.read_uint16()}')
                print(f'number of tables: TODO')
            elif command == '.tables':
                pass
            else:
                raise ValueError('Unknown dot command')
        else: # SQL query
            pass

    def unpack(self, fmt: str, size: int = 1):
        ret = struct.unpack(
            f'>{fmt}',
            self.read_bytes(size)
        )

        return ret[0] if len(ret) == 1 else ret

    def read_uint16(self):
        return self.unpack('H', 2)

    def read_bytes(self, size: int):
        return self.f.read(size)

    def read_byte(self):
        return self.read_bytes(1)

    def move(self, offset: int):
        self.f.seek(offset, os.SEEK_CUR)


def main() -> None:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('filename')
    arg_parser.add_argument('command')

    args = arg_parser.parse_args()

    with open(args.filename, 'rb') as f:
        sqlite = SQLiteFile(f)
        sqlite.exec(args.command)


if __name__ == '__main__':
    main()

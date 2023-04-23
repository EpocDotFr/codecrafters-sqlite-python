from typing import BinaryIO
import argparse
import struct


class SQLite:
    database: BinaryIO

    def __init__(self, database: BinaryIO):
        self.database = database

    def unpack(self, fmt, size=1):
        return struct.unpack(
            f'>{fmt}',
            self.database.read(size)
        )

    def exec(self, command: str) -> None:
        if command[0] == '.': # Dot command
            if command == '.dbinfo':
                self.database.seek(16)

                page_size = self.unpack('H', 2)[0]

                print(f'database page size: {page_size}')
                print(f'number of tables: TODO')
            elif command == '.tables':
                pass
            else:
                raise ValueError('Unknown command')
        else: # SQL query
            pass


def main() -> None:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('database', type=argparse.FileType('rb'))
    arg_parser.add_argument('command')

    args = arg_parser.parse_args()

    db = SQLite(args.database)
    db.exec(args.command)


if __name__ == '__main__':
    main()

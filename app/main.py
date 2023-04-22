from dataclasses import dataclass
import argparse
import sqlparse
import struct


def main() -> None:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('database', type=argparse.FileType('rb'))
    arg_parser.add_argument('command', choices=['.dbinfo'])

    args = arg_parser.parse_args()

    if args.command == '.dbinfo':
        args.database.seek(16)

        page_size = struct.unpack('>h', args.database.read(2))[0]

        print(f'database page size: {page_size}')

if __name__ == '__main__':
    main()

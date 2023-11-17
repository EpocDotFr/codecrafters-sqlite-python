from app.sqlite import SQLiteFile
import argparse


def main() -> None:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('filename')
    arg_parser.add_argument('command')

    args = arg_parser.parse_args()

    with open(args.filename, 'rb') as f:
        print(SQLiteFile.exec(f, args.command))


if __name__ == '__main__':
    main()

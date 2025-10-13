from app.enums import PageType, WriteVersion, ReadVersion, DatabaseTextEncoding
from typing import BinaryIO, Any, List, Optional
from io import SEEK_CUR, SEEK_SET
import struct


class SQLiteRecord:
    header_length: int
    serial_types = List[int]
    columns = List[Any]


class SQLiteCell:
    left_child_page_number: Optional[int]
    payload_bytes_count: Optional[int]
    rowid: Optional[int]
    payload: Optional[SQLiteRecord]
    first_overflow_page_page_number: Optional[int]


class SQLitePage:
    start: int
    page_type: PageType
    start_first_freeblock: int
    cells_count: int
    start_cell_content_area: int
    fragmented_bytes_count: int
    right_most_pointer: Optional[int]
    cell_offsets: List[int]
    cells: List[SQLiteCell]


class SQLiteFile:
    f: BinaryIO

    page_size: int
    write_version: WriteVersion
    read_version: ReadVersion
    reserved_space_size: int
    max_embed_payload_frac: int
    min_embed_payload_frac: int
    leaf_payload_frac: int
    file_change_counter: int
    db_size_pages: int
    first_freelist_page: int
    total_freelist_page: int
    schema_cookie: int
    schema_format_number: int
    default_page_cache_size: int
    largest_root_btree_page_number: int
    database_text_encoding: DatabaseTextEncoding
    user_version: int
    incr_vacuum_mode: int
    app_id: int
    version_valid_for_number: int
    sqlite_version_number: int

    pages: List[SQLitePage] = []

    def __init__(self, f: BinaryIO):
        self.f = f

        if self.read_bytes(16) != b'SQLite format 3\x00':
            raise ValueError('Not a SQLite file')

        self.read_first_page()

        # while True:
        #     page = self.read_page()
        #
        #     if not page:
        #         break
        #
        #     self.pages.append(page)

    def read_header(self) -> None:
        self.page_size = self.read_uint16()
        self.write_version = WriteVersion(self.read_uint8())
        self.read_version = ReadVersion(self.read_uint8())
        self.reserved_space_size = self.read_uint8()
        self.max_embed_payload_frac = self.read_uint8()
        self.min_embed_payload_frac = self.read_uint8()
        self.leaf_payload_frac = self.read_uint8()
        self.file_change_counter = self.read_uint32()
        self.db_size_pages = self.read_uint32()
        self.first_freelist_page = self.read_uint32()
        self.total_freelist_page = self.read_uint32()
        self.schema_cookie = self.read_uint32()
        self.schema_format_number = self.read_uint32()
        self.default_page_cache_size = self.read_uint32()
        self.largest_root_btree_page_number = self.read_uint32()
        self.database_text_encoding = DatabaseTextEncoding(self.read_uint32())
        self.user_version = self.read_uint32()
        self.incr_vacuum_mode = self.read_uint32()
        self.app_id = self.read_uint32()

        self.read_bytes(20) # Reserved space

        self.version_valid_for_number = self.read_uint32()
        self.sqlite_version_number = self.read_uint32()

    def read_first_page(self) -> None:
        self.read_header()

        page = SQLitePage()

        page.start = 0
        page.page_type = PageType(self.read_uint8())
        page.start_first_freeblock = self.read_uint16()
        page.cells_count = self.read_uint16() # FIXME For some reason does not find the correct amount of cells of the first page (3 instead or 5)
        page.start_cell_content_area = self.read_uint16()

        if page.start_cell_content_area == 0:
            page.start_cell_content_area = 65536

        page.fragmented_bytes_count = self.read_uint8()

        if page.page_type in (PageType.InteriorTable, PageType.InteriorIndex):
            page.right_most_pointer = self.read_uint32()

        page.cell_offsets = [
            self.read_uint16() for _ in range(page.cells_count)
        ]

        pos = self.tell()

        page.cells = [
            self.read_cell(page, offset) for offset in page.cell_offsets
        ]

        self.move_set(pos)

        self.pages.append(page)

    @classmethod
    def exec(cls, f: BinaryIO, command: str) -> str:
        sqlite = cls(f)

        if command[0] == '.': # Dot command
            if command == '.dbinfo':
                return sqlite.exec_dbinfo()
            elif command == '.tables':
                return sqlite.exec_tables()
            else:
                raise ValueError('Unknown dot command')
        else: # SQL query
            raise NotImplementedError()

    def exec_dbinfo(self) -> str:
        return '\n'.join((
            f'database page size: {self.page_size}',
            f'number of tables: {self.pages[0].cells_count}'
        ))

    def exec_tables(self) -> str:
        return ''

    def unpack(self, fmt: str, size: int = 1) -> Any:
        ret = struct.unpack(
            f'>{fmt}',
            self.read_bytes(size)
        )

        return ret[0] if len(ret) == 1 else ret

    def read_varint(self) -> int:
        bits = ''

        while True:
            byte_bits = format(self.read_uint8(), '08b')

            bits += byte_bits[1:]

            if byte_bits[0] == '0':
                break

        return int(bits, 2)

    def read_cell(self, page: SQLitePage, offset: int) -> SQLiteCell:
        cell = SQLiteCell()

        self.move_set(page.start + offset)

        if page.page_type in (PageType.InteriorTable, PageType.InteriorIndex):
            cell.left_child_page_number = self.read_uint32()

        if page.page_type in (PageType.LeafTable, PageType.LeafIndex, PageType.InteriorIndex):
            cell.payload_bytes_count = self.read_varint()

        if page.page_type in (PageType.LeafTable, PageType.InteriorTable):
            cell.rowid = self.read_varint()

        if page.page_type in (PageType.LeafTable, PageType.LeafIndex, PageType.InteriorIndex):
            cell.payload = SQLiteRecord()

            cell.payload.header_length = self.read_varint()
            cell.payload.serial_types = [
                self.read_varint() for _ in range(page.cells_count)
            ]

            cell.payload.columns = [
                self.read_column(serial_type) for serial_type in cell.payload.serial_types
            ]

            print(cell.payload.columns)

        if page.page_type in (PageType.LeafTable, PageType.LeafIndex, PageType.InteriorIndex):
            cell.first_overflow_page_page_number = self.read_uint32()

        return cell

    def read_column(self, serial_type: int) -> Any:
        if serial_type == 0:
            return None
        elif serial_type == 1:
            return self.read_uint8()
        elif serial_type == 2:
            return self.read_uint16()
        # elif serial_type == 3:
        #     return self.read_uint24()
        elif serial_type == 4:
            return self.read_uint32()
        # elif serial_type == 5:
        #     return self.read_uint48()
        elif serial_type == 6:
            return self.read_uint64()
        elif serial_type == 7:
            return self.read_float()
        elif serial_type == 8:
            return 0
        elif serial_type == 9:
            return 1
        elif serial_type >= 12 and serial_type % 2 == 0:
            return self.read_bytes(int((serial_type - 12) / 2))
        elif serial_type >= 13 and serial_type % 2 != 0:
            return self.read_bytes(int((serial_type - 13) / 2)).decode(
                self.database_text_encoding.python()
            )
        else:
            raise ValueError(f'Unhandled serial type {serial_type}')

    def read_uint8(self) -> int:
        return self.unpack('B')

    def read_uint16(self) -> int:
        return self.unpack('H', 2)

    def read_uint32(self) -> int:
        return self.unpack('I', 4)

    def read_uint64(self) -> int:
        return self.unpack('Q', 8)

    def read_float(self) -> float:
        return self.unpack('f', 4)

    def read_bytes(self, size: int) -> bytes:
        return self.f.read(size)

    def read_byte(self) -> bytes:
        return self.read_bytes(1)

    def tell(self) -> int:
        return self.f.tell()

    def move(self, offset: int) -> None:
        self.f.seek(offset, SEEK_CUR)

    def move_set(self, offset: int) -> None:
        self.f.seek(offset, SEEK_SET)

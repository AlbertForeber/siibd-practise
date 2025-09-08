import argparse
import binascii, calendar, base64, re, os
from typing import List

from errors import ParseError, DirectoryNotFound
from extra import MONTHS, EXTRA, DEBUG
from vfs.vfs_node import VFSNode


def parser(to_parse: str):
    parsed = to_parse.strip().split()
    for index, i in enumerate(parsed[1:]):
        if i[0] == '$':
            parsed_argument = re.match(r"\$(\w+)|\${([^}]+)}", i)
            var1, var2 = parsed_argument.groups()
            var_name = var1 or var2
            parsed[index + 1] = os.environ.get(var_name, "")

    return parsed[0], parsed[1:]


def handle_console_args():
    argument_parser = argparse.ArgumentParser(description="UNIX Emulator")
    argument_parser.add_argument("--version", action="version", version="Emulator 1.0")
    argument_parser.add_argument("vfs", help="VFS destination")
    argument_parser.add_argument("--script", dest='script', help="Start script destination")

    return argument_parser.parse_args()


def show_console_args(args: List[str]):
    parsed = vars(args)
    print('-' * 40)
    print(DEBUG.format(f"Received arguments:"))
    for key, value in parsed.items():
        print(f"+{DEBUG.format(key):>18}: {EXTRA.format(value)}")
    print('-' * 40)


def get_to_dir(command: str, root: VFSNode, source: str = ""):
    temp_root = root
    if source.startswith('/'):
        route = source.split('/')
        while temp_root.data.get('../..'):
            temp_root = temp_root.data['..']

    elif source.startswith('./'):
        route = source[2:].split('/')

    elif  source == '~' or not source:
        route = []
        while temp_root.data.get('../..'):
            temp_root = temp_root.data['..']

    elif source == '..':
        route = []
        parent = temp_root.data.get('../..')
        temp_root = parent if parent else temp_root

    else:
        route = source.split('/')

    for i in route:
        if not (temp_root := temp_root.data.get(i)):
            raise DirectoryNotFound(command, i)
    return temp_root


def decode_b64(to_decode: str):
    try:
        return base64.b64decode(to_decode, validate=True)
    except binascii.Error:
        raise ParseError("Wrong binary data")


def encode_b64(to_encode: bytes):
    return base64.b64encode(to_encode).decode()


def print_one_month(year, month):
    matrix = calendar.monthcalendar(year, month)
    print(f"{MONTHS[month - 1]:^21}")
    for i in (['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']):
        print(f'{i:>3}', end='')
    print()
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            print(f'{matrix[i][j] if matrix[i][j] != 0 else " ":>3}', end='')
        print()


def default_print(mx, target: VFSNode):
    for index, i in enumerate(target.data):
        if i == '..': continue
        if index != 0 and index % 4 == 0:
            print()
        print(f"{i:<{mx}}", end='')
    print()


def long_print(mx, target: VFSNode):
    print(EXTRA.format(f"№\t{'name:':<{mx}}file_type:"))
    for index, i in enumerate(target.data):
        if i != '..':
            print(f"{index + 1}.\t{i:<{mx}}{target.data[i].filetype}")
#
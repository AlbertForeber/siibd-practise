import getpass
import os
import re
import argparse
import calendar
import xml.etree.ElementTree as ET
from extra import *
import base64
from datetime import datetime

EMULATOR_START_TIME = datetime.now().strftime("%Y-%m-%d %H:%M")

# To register new commands
commands = {}


def register(name):
    def decorator(func):
        commands[name] = func
        return func

    return decorator


# Commands
@register("ls")
def ls(args=None):
    mx = max([len(x) for x in vfs_root.data]) + 2
    if args and args[0] == "-l":
        print(EXTRA.format(f"№\t{'name:':<{mx}}file_type:"))
        for index, i in enumerate(vfs_root.data):
            if i != '..':
                print(f"{index + 1}.\t{i:<{mx}}{vfs_root.data[i].filetype}")
    else:
        for index, i in enumerate(vfs_root.data):
            if i == '..': continue
            if index != 0 and index % 4 == 0:
                print()
            print(f"{i:<{mx}}", end='')
        print()



def pwd(node = None):
    if parent := vfs_root if not node else node.data.get('..'):
        for i in parent.data:
            if parent.data[i] == node:
                return pwd(parent) + i + '/'
    return '/'


@register("pwd")
def print_pwd():
    print(pwd())


@register("cd")
def cd(args=None):
    global vfs_root
    if args is None:
        temp_root = vfs_root
        while temp_root.data.get('..'):
            temp_root = temp_root.data['..']
        vfs_root = temp_root
    elif vfs_root.data.get(args[0]) and vfs_root.data[args[0]].filetype == 'dir':
        vfs_root = vfs_root.data[args[0]]
    elif args[0] != '..':
        raise IOError(f"cd: {args[0]}: No such directory")


@register("who")
def who():
    print(f"{getpass.getuser():<20}{os.ttyname(0):<20}{EMULATOR_START_TIME:<20}")


#Calendar
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


@register("cal")
def cal(args=None):
    if args:
        try:
            args = [int(i) for i in args]
            match len(args):
                case 1:
                    for i in range(1, 13):
                        print_one_month(args[0], i)
                case 2:
                    print_one_month(args[0], args[1])
                case _:
                    raise IOError(f"cal: {args}: wrong arguments amount")
        except Exception as e:
            raise IOError(f"cal: {args}: {e}")
    else:
        today = datetime.today()
        print_one_month(today.year, today.month)


@register("mkdir")
def mkdir(args):
    for i in args:
        vfs_root.data[i] = Node('dir', {})


@register("exit")
def exit_program():
    exit()


# Command interpreter
def get_input_call():
    result = f"{getpass.getuser()}@{os.uname()[1]}{pwd(vfs_root)}~%"
    return INPUT.format(result[:-2], result[-2:])


def parser(to_parse: str):
    parsed = to_parse.strip().split()
    for index, i in enumerate(parsed[1:]):
        if i[0] == '$':
            parsed_argument = re.match(r"\$(\w+)|\${([^}]+)}", i)
            var1, var2 = parsed_argument.groups()
            var_name = var1 or var2
            parsed[index + 1] = os.environ.get(var_name, "")

    return parsed[0], parsed[1:]


def command_executor(received_command: str, args):
    if received_command in commands:
        if not args:
            return commands[received_command]()
        else:
            return commands[received_command](args)
    else:
        raise IOError(f"Unknown command: {received_command}")


# Script
def script_executor(source: str):
    try:
        f = open(source)
    except:
        raise IOError(f"No such file: {source}")

    for i in f:
        if i[0] == '#':
            continue
        command, arguments = parser(i)
        print(get_input_call(), end=' ')
        print(command, *arguments)
        try:
            command_executor(command, arguments)
        except Exception as e:
            print(ERROR.format(e))


# VFS-xml
def from_xml(source: str):
    if not re.match(r'.+\.xml$', source):
        raise IOError('Wrong format')

    try:
        tree = ET.parse(source)
    except:
        raise IOError(f"No such file: {source}")

    root_element = tree.getroot()
    root: Node = Node('dir', {})
    build_node(root_element, root)
    return root


def build_node(parent_element, parent):
    for i in parent_element.findall('./'):
        file_type = i.get('type')
        new_node = None

        match file_type:
            case 'dir':
                new_node = Node('dir', {'..': parent})
                build_node(i, new_node)
            case 'binary':
                new_node = Node('binary', {'..': parent, 'data': decode_b64(i.attrib['data'])})
            case 'text':
                new_node = Node('text', {'..': parent, 'data': i.attrib['data']})

        parent.data[f'{i.tag}'] = new_node


# VFS-local
class Node:
    def __init__(self, filetype, data=None):
        self.filetype = filetype
        self.data = data

    def __str__(self):
        return f"Node(filetype: {self.filetype}, attr: {self.data})"


# VFS-binary
def decode_b64(to_decode: str):
    return base64.b64decode(to_decode)


def encode_b64(to_encode: bytes):
    return base64.b64encode(to_encode).decode()

# Emulator
def emulate():
    while True:
        print(get_input_call(), end=' ')
        inp = input().strip()

        if not inp:
            continue
        command, arguments = parser(inp)

        try:
            command_executor(command, arguments)
        except Exception as e:
           print(ERROR.format(e))


# Console arguments interpreter
def handle_console_args():
    argument_parser = argparse.ArgumentParser()

    argument_parser.add_argument("--version", action="version", version="Emulator 1.0")
    argument_parser.add_argument("vfs", help="VFS destination")
    argument_parser.add_argument("--script", dest='script', help="Start script destination")

    return argument_parser.parse_args()


def show_console_args(args):
    parsed = vars(args)
    print('-'*40)
    print(DEBUG.format(f"Received arguments:"))
    for key, value in parsed.items():
        print(f"+{DEBUG.format(key):>18}: {EXTRA.format(value)}")
    print('-'*40)


# Main function
def start_up():

    # Handling scripts
    if console_args.script:
        script_executor(console_args.script)
    else:
        emulate()


# Initializing VFS
try:
    console_args = handle_console_args()
    show_console_args(console_args)
    vfs_root = from_xml(console_args.vfs)
except Exception as e:
    print(ERROR.format(e))

start_up()



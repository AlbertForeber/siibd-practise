import getpass
import os
import re
import argparse
import xml.etree.ElementTree as ET
from colors import *
import base64

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
    def ls(args=None):
        print("ls")
        if args:
            for i in args:
                print(i)



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
def cd(args = None):
    print("cd")
    if args:
        for i in args:
            print(i)



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
            return


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
    print(DEBUG.format(f"Received arguments"))
    for key, value in parsed.items():
        print(f"+{DEBUG.format(key):>18}: {DEBUG.format(value)}")


# Main function
def start_up():

    # Handling scripts
    if args.script:
        script_executor(args.script)
    else:
        emulate()

# Initializing VFS

try:
    args = handle_console_args()
    show_console_args(args)
    vfs_root = from_xml(args.vfs)

    start_up()
except Exception as e:
    print(ERROR.format(e))





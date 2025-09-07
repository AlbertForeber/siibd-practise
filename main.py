import getpass
import os
import re
import argparse
import xml.etree.ElementTree as ET
from colors import *

# To register new commands
commands = {}
vfs_root = ""

def register(name):
    def decorator(func):
        commands[name] = func
        return func
    return decorator


# Commands
@register("ls")
def ls(args = None):
    print("ls")
    if args:
        for i in args:
            print(i)


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
    result = f"{getpass.getuser()}@{os.uname()[1]}~%"
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


# Main function
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


# Main function
def start_up():
    args = handle_console_args()
    print(DEBUG.format(f"Received arguments: ${args.vfs} {args.script}".replace(f"{None}", "")))

    # Handling scripts
    if args.script:
        try:
            script_executor(args.script)
        except Exception as e:
            print(ERROR.format(e))
            return
    else:
        emulate()

start_up()



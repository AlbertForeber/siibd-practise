import getpass
import os
import re

commands = {}

def register(name):
    def decorator(func):
        commands[name] = func
        return func
    return decorator


@register("ls")
def ls(args):
    print("Command: ls. Arguments:", end=' ')
    for i in args:
        print(i, end='; ')
    print()


@register("cd")
def cd(args):
    print("Command: cd. Arguments:", end=' ')
    for i in args:
        print(i, end = '; ')
    print()


@register("exit")
def exit_program():
    exit()


def get_input_call():
    return f"{getpass.getuser()}@{os.uname()[1]}~%"


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
    if not args:
        return commands[received_command]()
    else:
        return commands[received_command](args)


def emulate():
    while True:
        print(get_input_call(), end=' ')

        inp = input().strip()

        if not inp:
            continue
        command, arguments = parser(inp)

        command_executor(command, arguments)

emulate()
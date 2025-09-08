import getpass
import os
from datetime import datetime
from typing import List, Optional

from errors import WrongArguments, UnknownCommand
from utils import *
from vfs import VFS

EMULATOR_START_TIME = datetime.now().strftime("%Y-%m-%d %H:%M")


commands = {}   # имя_функции - функция
params = {}     # имя_функции - [необходимое кол-во арг-ов, максимальное кол-во арг-ов]


class CommandHandler:
    def __init__(self, vfs: VFS):
        self.vfs = vfs

    @staticmethod
    def register(name, min_param: int, max_param: int):
        def decorator(func):
            commands[name] = func
            params[name] = [min_param, max_param]
            return func
        return decorator


    @register(name="ls", min_param=0, max_param=2)
    def ls(self, args: Optional[List[str]] = None):
        target = self.vfs.current_directory

        # Берем самое длинное название файла для расчета отступов
        mx = max([len(x) for x in self.vfs.current_directory.data]) + 2

        if args:
            if args[-1] != "-l":
                target = get_to_dir('ls', target, args[-1])
                mx = max([len(x) for x in target.data]) + 2
            if args[0] == "-l":
                long_print(mx, target)
            else:
                default_print(mx, target)
        else:
            default_print(mx, target)


    def pwd(self, node=None):
        if parent := self.vfs.current_directory if not node else node.data.get('..'):
            for i in parent.data:
                if parent.data[i] == node:
                    return self.pwd(parent) + i + '/'
        return '/'


    @register("pwd", 0, 0)
    def print_pwd(self):
        print(self.pwd())


    @register("cd", 0, 1)
    def cd(self, args: Optional[List[str]] = None):
        arg = args[0] if args else ''
        self.vfs.current_directory = get_to_dir('cd', self.vfs.current_directory, arg)


    @register("who", 0, 0)
    def who(self):
        print(f"{getpass.getuser():<20}{os.ttyname(0):<20}{EMULATOR_START_TIME:<20}")

    # Calendar
    @register("cal", 0, 2)
    def cal(self, args=None):
        if args:
            try:
                args = [int(i) for i in args]
                match len(args):
                    case 1:
                        for i in range(1, 13):
                            print_one_month(args[0], i)
                    case 2:
                        print_one_month(args[0], args[1])
            except Exception as e:
                raise WrongArguments('cal', f"{e}")
        else:
            today = datetime.today()
            print_one_month(today.year, today.month)

    @register("mkdir", 1, 1)
    def mkdir(self, args):
        for i in args:
            self.vfs.current_directory.data[i] = VFSNode(i, 'dir', {})

    @register("exit", 0, 0)
    def exit_program(self, args):
        exit()

    def command_executor(self, received_command: str, args):
        if received_command in commands:
            min_args, max_args = params[received_command]
            if min_args <= len(args) <= max_args:
                return commands[received_command](self, args)
            else:
                raise (
                    WrongArguments(
                        received_command,
                     f"got {len(args)} arguments when from {min_args} to {max_args} expected")
                )
        else:
            raise UnknownCommand(received_command)
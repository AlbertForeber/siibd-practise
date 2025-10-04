import getpass
import os

from errors import VFSError
from utils import handle_console_args, show_console_args, parser

from commands import CommandHandler
from extra import *

from vfs import VFS


class Emulator:
    def __init__(self):
        self.vfs = VFS()
        self.commandHandler = CommandHandler(self.vfs)
        self.params = handle_console_args()
        show_console_args(self.params)


    def __init_vfs(self):
        try:
            self.vfs.from_xml(self.params.vfs)
        except VFSError as e:
            print(e)
            exit(1)


    # Get string representation of user info and current path
    def __get_input_call(self):
        cur_path = self.commandHandler.pwd()
        result = f"{getpass.getuser()}@{os.uname()[1]}{cur_path}~%"
        return INPUT.format(result[:-2], result[-2:])


    # Script handler
    def __script_executor(self, source: str):
        try:
            f = open(source)
        except FileNotFoundError:
            print(f"No such file: {source}")
            exit(1)

        for i in f:
            if i[0] == '#':
                continue
            command, arguments = parser(i)

            print(self.__get_input_call(), end=' ')
            print(command, *arguments)

            try:
                self.commandHandler.command_executor(command, arguments)
            except Exception as e:
                print(ERROR.format(e))

    # Emulator
    def __emulate(self):
        while True:
            print(self.__get_input_call(), end=' ')
            inp = input().strip()

            if not inp:
                continue
            command, arguments = parser(inp)

            try:
                self.commandHandler.command_executor(command, arguments)
            except Exception as e:
                print(ERROR.format(e))


    def start_up(self):
        self.__init_vfs()

        # Handling scripts
        if self.params.script:
            self.__script_executor(self.params.script)
        # No-script mode
        else:
            self.__emulate()


if __name__ == '__main__':
    emu = Emulator()
    emu.start_up()
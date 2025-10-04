# VFS Errors
class VFSError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class WrongFormatError(VFSError):
    def __init__(self, source):
        super().__init__(f"File {source} is not XML-file")


class VFSNotFoundError(VFSError):
    def __init__(self, source):
        super().__init__(f"No such file: {source}")


class ParseError(VFSError):
    def __init__(self, source):
        super().__init__(f"An error occurred while parsing: {source}")


# Command Errors
class CommandError(Exception):
    def __init__(self, command, message):
        self.message = message
        super().__init__(f"{command}: {message}")


class WrongArguments(CommandError):
    def __init__(self, command, *args):
        wrong_args = ' '.join(args)
        super().__init__(command, f"wrong arguments: {wrong_args}")


class DirectoryNotFound(CommandError):
    def __init__(self, command, path):
        super().__init__(command, f"no such directory: {path}")


class UnknownCommand(CommandError):
    def __init__(self, command):
        super().__init__(command, f"command not found")
#
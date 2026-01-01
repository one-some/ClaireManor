from __future__ import annotations

# File has to be split to prevent circular import >_>

class CommandMeta(type):
    @staticmethod
    def format_command(cmd: Command | type) -> str:
        out = []

        for option_set in cmd.pattern:
            clean = []
            if not isinstance(option_set, list):
                clean.append("str")
            else:
                for bit in option_set:
                    # FUTURE: Add Location, Item, etc support
                    assert isinstance(bit, str)
                    clean.append(bit)
            out.append("[%s]" % "/".join(clean))

        return " ".join(out)

    def __str__(self) -> str:
        return CommandMeta.format_command(self)

class Command(metaclass=CommandMeta):
    pattern = [[]]
    description = ""

    def __init__(self) -> None:
        raise NotImplementedError

    @staticmethod
    async def execute(arguments: list) -> None:
        raise NotImplementedError

class LocalCommand(Command):
    def __init__(self, arg_pattern: list[list], execute: callable) -> None:
        self.pattern = arg_pattern
        self.execute = execute

    def __repr__(self) -> str:
        return CommandMeta.format_command(self)

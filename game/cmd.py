import asyncio
import pyray as rl

from ui.text import RichTextChunk
from game.io import print_line, prompt
from etc.utils import get_subclasses
from game.player import Player

class Location:
    name = ". . ."
    description = ". . ."

    commands = []
    objects = []

class Command:
    pattern = [[]]
    description = ". . ."

    def __init__(self) -> None:
        raise NotImplementedError

    @staticmethod
    async def execute(arguments: list) -> None:
        raise NotImplementedError

    @classmethod
    def to_str(cls) -> str:
        # NOTE: Can't use __str__ here because there are no instances of
        # commands. At least I don't THINK theres a way to do __str__ on
        # classes... my WiFi is down. Maybe some abstractbaseclass stuff
        out = []

        for option_set in cls.pattern:
            clean = []
            for bit in option_set:
                # FUTURE: Add Location, Item, etc support
                assert isinstance(bit, str)
                clean.append(bit)
            out.append("[%s]" % "/".join(clean))

        return " ".join(out)


class HelpCommand(Command):
    pattern = [["?", "help"]]
    description = "Lists all commands (this menu!)"

    @staticmethod
    async def execute(arguments: list) -> None:
        await print_line("-- Help --")
        for command in commands:
            await print_line(f"{command.to_str()} - {command.description}")

class ExitCommand(Command):
    pattern = [["quit", "exit", "bye"]]
    description = "Exits the game, if you insist."

    @staticmethod
    async def execute(arguments: list) -> None:
        await print_line("Really leave?")
        if (await prompt("[yes/no]")).lower()[0] != "y":
            await print_line("Okay, then.")
            return

        await print_line("Bye!")
        await asyncio.sleep(0.5)
        exit(0)

commands = get_subclasses(Command)

def parse_for_command(command: Command, arg_str: str) -> list:
    args = []
    expectations = list(command.pattern[1:])

    while expectations:
        expectation = expectations.pop(0)
        pass

    return args

async def run_command(command_line: str) -> None:
    await print_line(" ")

    await print_line(RichTextChunk(
        f"> {command_line}",
        color=rl.Color(0xFF, 0xFF, 0xBB, 0xFF)
    ))

    command_line = command_line.lower()

    alias_to_command = {}
    for command in commands:
        for alias in command.pattern[0]:
            alias_to_command[alias] = command

    # Leading option search (longest to shortest; match "look at" before "look")
    alias_to_command = dict(sorted(
        alias_to_command.items(),
        key=lambda x: len(x[0]),
        reverse=True
    ))

    for starter, command in alias_to_command.items():
        # Of course it's gotta be this annoying because we're not just splitting
        # at spaces and matching. Do I even know if I will have commands with
        # spaces in them? Nope!
        if not command_line.startswith(starter): continue

        arg_str = command_line[len(starter):].strip()
        args = parse_for_command(command, arg_str)
        await command.execute(args)

        break
    else:
        # TODO: More helpful errors with like Levenshtein distance
        await print_line("Huh? I don't get that command. Try asking for <act>help</act>.")


import asyncio
import pyray as rl

from ui.text import RichTextChunk
from game.io import print_line, prompt
from etc.utils import get_subclasses
from game.player import Player

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
            if not isinstance(option_set, list):
                clean.append("str")
            else:
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

class MoveCommand(Command):
    pattern = [["move", "go", "goto", "walk"], str]
    description = "Walk into another room."

    @staticmethod
    async def execute(arguments: list) -> None:
        loc_query = arguments[0].lower()

        pathways = Player.player.location.pathways
        location_kv = {
            **{k.lower(): v for k, v in pathways.items()},
            **{v.name.lower(): v for v in pathways.values()},
        }
        print(location_kv)

        # Try to squish it until it works. These have to be seperate loops bc
        # they are prioritized
        if loc_query not in location_kv:
            # First, check if *we* start with a location. Maybe a player typed
            # the whole display string (???)
            for k in location_kv:
                if loc_query.startswith(k):
                    loc_query = k
                    break
            else:
                # Otherwise, let's assume the player is using a shortcut. Maybe
                # a location starts with *us*.
                for k in location_kv:
                    if k.startswith(loc_query):
                        loc_query = k
                        break

        if loc_query in location_kv:
            Player.player.location = location_kv[loc_query]
            await print_line(f"You go to {Player.player.location.display_name}")
        else:
            await print_line(f"I don't know where '{loc_query}' is. Take a look around:")
            for route, location in pathways.items():
                await print_line(f"- There is a <paleyellow>{route}</paleyellow> to {location.display_name} here.")

class LookCommand(Command):
    # Old habits die hard
    pattern = [["look", "ls"]]
    description = "Describes the room around you."

    @staticmethod
    async def execute(arguments: list) -> None:
        await Player.player.location.describe()

commands = get_subclasses(Command)

def parse_for_command(command: Command, arg_str: str) -> list:
    # FIXME: Please finish this
    args = []
    expectations = list(command.pattern[1:])

    while expectations:
        expectation = expectations.pop(0)
        if expectation == str:
            print("[WARNING!] Wildcard expectation ignores at least one following")
            args.append(arg_str)
            break
        else:
            assert False

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


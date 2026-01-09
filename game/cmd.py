import asyncio
import pyray as rl
from typing import Optional, Any

from ui.text import RichTextChunk
from game.io import print_line, prompt
from game.items.item import Item
from game.player import Player
from game.cmd_base import Command
from etc.utils import get_subclasses

def db_lookup(kv: dict, query: str) -> Optional[Any]:
    query = query.lower()
    kv = {k.lower(): v for k, v in kv.items()}

    # Longest to shortest for substring priority
    kv = dict(sorted(kv.items(), key=lambda x: x[0], reverse=True))

    if query in kv:
        return kv[query]

    if not query:
        return None

    # Try to squish it until it works. These have to be seperate loops bc
    # they are prioritized

    # First, check if *we* start with a location. Maybe a player typed
    # the whole display string (???)
    for k in kv:
        if query.startswith(k):
            return kv[k]

    # Next, let's assume the player is using a shortcut. Maybe
    # a location starts with *us*.
    for k in kv:
        if k.startswith(query):
            return kv[k]

    # Okay, maybe they're using a substring? Probs false positives, ensure we're
    # already sorted.
    print(kv, query)
    for k in kv:
        if query in k:
            return kv[k]

    # Idk
    return None

class HelpCommand(Command):
    pattern = [["?", "help"]]
    description = "Lists all commands (this menu!)"

    @staticmethod
    async def execute(arguments: list) -> None:
        await print_line("-- Help --")
        for command in commands:
            if not command.pattern[0]:
                continue
            await print_line(f"{command} - {command.description}")

        await print_line("<yellow>NOTE: Some commands are dependant on being near an object or location.</yellow>")
        await print_line("<yellow>Those will not be shown here. <act>look</act> or <act>inspect</act> your surroundings to</yellow>")
        await print_line("<yellow>see these actions.</yellow>")

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
            **{k: v for k, v in pathways.items()},
            **{v.name: v for v in pathways.values()},
        }

        maybe_location = db_lookup(location_kv, loc_query)

        if not maybe_location:
            await print_line(f"I don't know where '{loc_query}' is. Take a look around:")
            for route, location in pathways.items():
                await print_line(f"- There is a <paleyellow>{route}</paleyellow> to {location.display_name} here.")
            return

        await print_line(f"You're on your way.")
        await Player.player.set_location(maybe_location)

class InspectCommand(Command):
    pattern = [["look", "ls", "inspect"], str]
    description = "Inspects something. Inspect nothing to see the room around you, or an item/object"

    @staticmethod
    async def execute(arguments: list) -> None:
        if not arguments[0]:
            await Player.player.location.describe()
            return
        query = arguments[0].lower()

        targets = {}
        for obj in Player.player.location.objects:
            targets[obj.name] = obj
            for items in obj.item_locations.values():
                for item in items:
                    targets[item.name] = item

        print(targets)
        target = db_lookup(targets, query)

        if not target:
            await print_line(f"I don't know what '{query}' is. Take a look around:")
            for obj in Player.player.location.objects:
                await print_line(f"<gray>-</gray> There is {obj.article} {obj.display_name} here.")
                for relation, items in obj.item_locations.items():
                    for item in items:
                        await print_line(f"    <gray>-</gray> {relation.title()} the {obj.display_name}, there is a {item.name}.")
            return
        
        if isinstance(target, Item):
            await print_line(f"You look at the {target.name}.")
            desc = target.description or "There isn't much to see here."
            await print_line(desc)
            return

        await target.describe()

# class TakeCommand(Command):
#     pattern = [["grab", "get", "take", "collect"], str]
#     description = "Collects an item in the room"
# 
#     @staticmethod
#     async def execute(arguments: list) -> None:
#         query = arguments[0].lower()
# 
#         # TODO
# 
#         kv = {
#         }
# 
#         maybe = db_lookup(location_kv, loc_query)
# 
#         if not maybe:
#             await print_line(f"I don't know what '{query}' is. Maybe <act>look</act> around?")
#             return
#         
#         #TODO: PICKUP

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
    for command in commands + Player.player.location.applicable_commands():
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


from __future__ import annotations

import asyncio
from typing import Optional

from etc.utils import get_subclasses
from game import language
from game.io import print_line
from game.items.item import Item
from game.items.items import LeatherCoat, TragedyMask, ComedyMask, DarcyNote, EvilYarn
from game.items.weapon import Sword
from game.cmd_base import LocalCommand
from game.combat.combatant import EnemyAppearance, SkeletonCombatant, RatCombatant

class RoomObject:
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        commands: Optional[list[LocalCommand]] = None,
        item_locations: Optional[dict[str, Item]] = None,
    ) -> None:
        self.name = name
        self.description = description
        self.commands = commands or []
        self.item_locations = item_locations or {}

    @property
    def display_name(self) -> str:
        return f"<paleblue>{self.name}</paleblue>"

    @property
    def article(self) -> str:
        return language.indefinite_article(self.name)

    @property
    def display_description(self) -> str:
        return self.description or "It's unremarkable."

    async def describe(self) -> None:
        await print_line(self.display_name)
        await print_line(self.display_description)

        if self.commands:
            await print_line(f"<gray>You can do stuff with the {self.display_name}:</gray>")
        for command in self.commands:
            await print_line(f"<gray>-</gray> <act>{command}</act>")


        if self.item_locations:
            await print_line(f"<gray>You see some stuff here:</gray>")
        for relation, items in self.item_locations.items():
            for item in items:
                await print_line(f"<gray>-</gray> {relation.title()} the {self.display_name}, there is a {item.name}.")


# Never actually used metaclasses before. Exciting!! This lets us set getters
# on the actual class itself
class LocationMeta(type):
    locations = {}

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)
        mcs.locations[name] = new_class
        return new_class

    @property
    def display_name(self) -> str:
        return f"<yellow>{self.name} ({self.floor}F)</yellow>"

    @property
    def article(self) -> str:
        return language.indefinite_article(self.name)

    @property
    def display_description(self) -> str:
        if self.description:
            return f"<palegreen>{self.description}</palegreen>"
        return "<gray>It's unremarkable.</gray>"

    @property
    def enemy_pool(self) -> list[EnemyAppearance]:
        return self.additional_enemies + [
            EnemyAppearance(SkeletonCombatant),
            EnemyAppearance(RatCombatant),
        ]

class Location(metaclass=LocationMeta):
    name = ". . ."
    description = None

    floor = 0

    pathways = {}
    commands = []
    objects = []

    additional_enemies = []

    @staticmethod
    def lookup(name: str) -> Location:
        return LocationMeta.locations[name]

    @classmethod
    async def describe(cls) -> None:
        await print_line(f"You look around the {cls.display_name}.")
        await print_line(cls.display_description)

        if cls.pathways:
            await print_line(f"<gray>You can move from here:</gray>")
        for route, location in cls.pathways.items():
            article = language.indefinite_article(route)
            await print_line(f"- There is {article} <paleyellow>{route}</paleyellow> to {location.display_name} here.")

        if cls.objects:
            await print_line(f"<gray>You see some stuff here:</gray>")
        for obj in cls.objects:
            await print_line(f"<gray>-</gray> There is {obj.article} {obj.display_name} here.")
            for relation, items in obj.item_locations.items():
                for item in items:
                    await print_line(f"    <gray>-</gray> {relation.title()} the {obj.display_name}, there is a {item.name}.")

    @classmethod
    def applicable_commands(cls) -> list[LocalCommand]:
        out = []

        for obj in cls.objects:
            out += obj.commands

        return out

class EntrywayLocation(Location):
    name = "Entryway"
    description = "Every surface in the entryway is coated in dust. You do not feel any draft coming through the doorway."
    floor = 0

    pathways = {
        "arched entrance": "AntechamberLocation"
    }

    @staticmethod
    async def exec_open(arguments: list) -> None:
        await print_line("The door refuses to budge. You slam your body's full weight against it, and still nothing.")

    objects = [
        RoomObject(
            "Door",
            description="The door looks old and decayed, but doesn't seem to be going anywhere soon.",
            commands=[
                LocalCommand(
                    [["open"]],
                    exec_open
                )
            ],
        ),
        RoomObject(
            "Coatrack",
            description="An old coatrack.",
            item_locations={
                "on": [
                    LeatherCoat()
                ]
            }
        )
    ]

class AntechamberLocation(Location):
    name = "Antechamber"
    description = "The heart of the house; all other rooms seem to branch out from here. The room itself is oddly sparse, and smells strongly of peat moss. Cobwebs gently adorn the chandelier, which hovers above a weird clump of carpet. You could rest here."
    floor = 0

    pathways = {
        "arched exit": "EntrywayLocation",
        "ever-open doorway": "EastHallLocation",
    }

    @staticmethod
    async def exec_rest(arguments: list) -> None:
        # I have done a lot of bad things in my life, but also some good. Please ignore the next
        # line if you have a heart.
        from game.player import Player

        await print_line("You clumsily lower your body onto the pile of carpet. It chafes against your skin, but after a while, exhaustion overtakes you.")
        Player.player.save()
        await asyncio.sleep(1.0)
        await print_line("...")
        await asyncio.sleep(1.0)
        await print_line("You awaken after some time. You aren't sure how much time has passed, but you feel well rested.")
        await asyncio.sleep(1.0)
        await print_line("<yellow>You saved the game!</yellow>")

    objects = [
        RoomObject(
            "Makeshift Bed",
            description="There is an old roll of carpet here. It's unclear why, but it could function as a bed in a pinch. [<yellow>Save Location</yellow>]",
            commands=[
                LocalCommand(
                    [["rest", "sleep", "save"]],
                    exec_rest
                )
            ],
        )
    ]


class EastHallLocation(Location):
    name = "East Hall"
    description = "The long eastern hallway has striped wallpaper, making the hall appear taller than it actually is. As of recently, though, the wallpaper is peeling due to water damage. A lonely vase sits on the table at the end of the hall."
    floor = 0

    @staticmethod
    async def exec_fish_vase(arguments: list) -> None:
        await print_line("You plunge your hand into the cold water of the vase and begin to fish around.")
        await asyncio.sleep(1.0)
        await print_line("...")
        await asyncio.sleep(1.0)
        await print_line("<red>You feel something cold and hard. You pull out a human finger.</red>")
        await asyncio.sleep(1.0)
        await print_line("You return it. Perhaps it was sleeping.")

    pathways = {
        "ever-open doorway": "AntechamberLocation",
        "beckoningly ajar doorway": "BoudoirLocation",
        "swinging door": "KitchenLocation",
        "grand doorway": "DiningHallLocation",
    }

    objects = [
        RoomObject(
            "Vase",
            description="Whatever flowers were once in this vase have long disintigrated, but somehow the water remains. <yellow>You see something in the bottom of the water.</yellow>",
            commands=[
                LocalCommand(
                    [["fish"]],
                    exec_fish_vase
                )
            ],
        ),
    ]

class BoudoirLocation(Location):
    name = "Boudoir"
    description = "The powdery air of the boudoir seems to linger after what seems to be decades of disuse. Many objects throughout the room feel out of place in a way that makes you deeply uncomfortable, almost primally so. You are on high alert."
    floor = 0

    pathways = {
        "hope of escape": "EastHallLocation"
    }

    objects = [
        RoomObject(
            "Pink Chair",
            description="For all the discomfort the Boudoir brings you, this chair looks incredibly comfortable. Which is odd, considering it's a glorified lawn chair. You aren't able to reason about your feelings for the chair.",
        ),
        RoomObject(
            "Round Table",
            description="A medium-sized roundtable. It is the perfect size for a small gathering between close friends, though the scoring and burn marks on the table seem rather uninviting.",
            item_locations={
                "atop": [
                    TragedyMask(),
                    ComedyMask(),
                ]
            }
        )
    ]

class KitchenLocation(Location):
    name = "Kitchen"
    description = "Immediately upon entering the kitchen you are confronted by a vile miasma. The stench of untempered rot floods your sinuses and you are briefly disoriented. As you come to your senses you're greeted with a small room floored with some sort of checkered proto-linoleum. Mid-completion courses sit decaying on the countertop as if those responsible for finalizing them simply vanished into thin air."
    floor = 0

    pathways = {
        "swinging door": "EastHallLocation",
        "discrete double doors": "DiningHallLocation",
    }

    objects = [
        RoomObject(
            "Barrel",
            description="The room's stench seems to either concentrate around or eminate from this barrel. The body of the barrel is so severely swolen you fear that the corroded loops will give soon. Pressure builds from within; something is rotting inside.",
        ),
    ]

class DiningHallLocation(Location):
    name = "Dining Hall"
    description = "The dining hall is vast, with tall coved ceilings. You hear an echo as your shoes tap against the checkered marble floor."
    floor = 0

    pathways = {
        "grand doorway": "EastHallLocation",
        "discrete double doors": "KitchenLocation",
        "sturdy wooden door": "MudRoomLocation",
    }

    objects = [
        RoomObject(
            "Chairs",
            description="The chairs around the table are all pulled out. It infuriates you!",
        ),
        RoomObject(
            "Yellowed Plate",
            description="The dining table is set, but one plate is significantly more yellowed than the rest.",
            # TODO: Hidden. Note
            item_locations={
                "under": [
                    DarcyNote(),
                ]
            }
        ),
    ]

class MudRoomLocation(Location):
    name = "Mud Room"
    description = "Your attention is immediately drawn to the red yarn sprawling across the floor. You can barely make out the floor's original tiling. Unraveled piles grow feet tall."
    floor = 0

    pathways = {
        "sturdy wooden door": "DiningHallLocation",
    }

    objects = [
        RoomObject(
            "Floor",
            description="It's covered in red yarn!",
            item_locations={
                "atop": [
                    EvilYarn(),
                ]
            }
        ),
    ]


# Hydrate first
for location in [Location] + get_subclasses(Location):
    for k, v in location.pathways.items():
        assert v in LocationMeta.locations, f"Invalid location classname '{v}'!"
        location.pathways[k] = LocationMeta.locations[v]

# Check at runtime for one-way rooms (these aren't intentional at this point!)
for location in [Location] + get_subclasses(Location):
    for other_loc in location.pathways.values():
        assert location in other_loc.pathways.values(), f"One-way room: {other_loc.__name__} doesn't reference {location.__name__}!"

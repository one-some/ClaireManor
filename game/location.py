from __future__ import annotations

from typing import Optional

from etc.utils import get_subclasses
from game.io import print_line
from game.items.item import Item
from game.items.weapon import Sword

class RoomObject:
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        item_locations: Optional[dict[str, Item]] = None,
    ) -> None:
        self.name = name
        self._description = description
        self.item_locations = item_locations or {}

    @property
    def display_name(self) -> str:
        return f"<paleblue>{self.name}</paleblue>"

    @property
    def description(self) -> str:
        return self._description or "It's unremarkable."

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
        return f"[<yellow>{self.name} ({self.floor}F)</yellow>]"

    @property
    def display_description(self) -> str:
        if self.description:
            return f"<palegreen>{self.description}</palegreen>"
        return "<gray>It's unremarkable.</gray>"

class Location(metaclass=LocationMeta):
    name = ". . ."
    description = None

    floor = 0

    pathways = {}
    commands = []
    objects = []

    @staticmethod
    def lookup(name: str) -> Location:
        return LocationMeta.locations[name]

    @classmethod
    async def describe(cls) -> None:
        await print_line(cls.display_name)
        await print_line(cls.display_description)

        if cls.objects:
            await print_line(f"<gray>You see some stuff here:</gray>")
        for obj in cls.objects:
            # TODO: A/An
            await print_line(f"<gray>-</gray> There is a {obj.display_name} here.")
            for relation, items in obj.item_locations.items():
                for item in items:
                    await print_line(f"    <gray>-</gray> {relation.title()} the {obj.display_name}, there is a {item.name}.")

        if cls.pathways:
            await print_line(f"<gray>You can move from here:</gray>")
        for route, location in cls.pathways.items():
            await print_line(f"- There is a <paleyellow>{route}</paleyellow> to {location.display_name} here.")

class EntrywayLocation(Location):
    name = "Entryway"
    description = "Every surface in the entryway is coated in dust. You do not feel any draft coming through the doorway."
    floor = 0

    pathways = {
        "archway": "AntechamberLocation"
    }

    objects = [
        RoomObject(
            "Door",
            description="The door looks old and decayed, but it won't budge.",
        ),
        RoomObject(
            "Coatrack",
            description="An old coatrack.",
            item_locations={
                "on": [
                    Sword()
                ]
            }
        )
    ]

class AntechamberLocation(Location):
    name = "Antechamber"
    description = "The heart of the floor. All other rooms seem to branch out from here. The room itself is oddly sparse."
    floor = 0

    pathways = {
        "archway": "EntrywayLocation"
    }

    objects = []

# Hydrate first
for location in [Location] + list(get_subclasses(Location)):
    for k, v in location.pathways.items():
        assert v in LocationMeta.locations, f"Invalid location classname '{v}'!"
        location.pathways[k] = LocationMeta.locations[v]

# Check at runtime for one-way rooms (these aren't intentional at this point!)
for location in [Location] + list(get_subclasses(Location)):
    for other_loc in location.pathways.values():
        assert location in other_loc.pathways.values(), f"One-way room: {other_loc.__name__} doesn't reference {location.__name__}!"

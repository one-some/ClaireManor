from game.io import print_line

class RoomObject:
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        item_locations: Optional[dict[str, Item]] = None,
    ) -> None:
        self.name = name
        self._description = self.description
        self.item_locations = item_locations or {}

    @property
    def description(self) -> str:
        return self._description or "It's unremarkable."

# Never actually used metaclasses before. Exciting!! This lets us set getters
# on the actual class itself
class LocationMeta(type):
    @property
    def display_name(self) -> str:
        return f"{self.name} | {self.floor}F"

    @property
    def display_description(self) -> str:
        return self.description or "It's unremarkable."

class Location(metaclass=LocationMeta):
    name = ". . ."
    description = None

    floor = 0

    neighbors = []
    commands = []
    objects = []

    @classmethod
    async def describe(cls) -> None:
        await print_line(cls.display_name)
        await print_line(cls.display_description)

        for obj in cls.objects:
            # TODO: A/An
            await print_line(f"There is a {obj.name}.")
            for relation, item in obj.item_locations.items():
                await print_line(f"- {relation.title()} the {obj.name}, there is a {item.name}.")

class EntrywayLocation(Location):
    name = "Entryway"
    description = "Every surface in the entryway is coated in dust. You do not feel any draft coming through the doorway."
    floor = 0

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

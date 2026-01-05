from game.items.item import Item
from game.items.weapon import Weapon

# This gets its own class because I don't want to accidentally reassign a list.
# I figure it'll be a whole lot harder if I can't slice or do comprehensions
# without thinking about it
class Inventory:
    def __init__(self, items: list[Item]) -> None:
        self.items = items

    def append(self, item: Item) -> None:
        self.items.append(item)

    @property
    def weapons(self) -> list[Weapon]:
        return [item for item in self.items if isinstance(item, Weapon)]

    @property
    def non_weapons(self) -> list[Item]:
        # Ooookay this is a litttttle weird
        return [item for item in self.items if not isinstance(item, Weapon)]

    def __iter__(self):
        yield from self.items

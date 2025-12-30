from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from game.combat.combatant import Combatant

class Item:
    base_name = "Unknown Item"
    format_pattern = "<blue>%s</blue>"
    static_actions = []

    @property
    def name(self) -> str:
        # TODO: Attributes
        return self.format_pattern % self.base_name

    @property
    def list_formatted(self) -> str:
        etc = ", ".join([a.name for a in self.static_actions])
        return f"{self.name} ({etc or '...'})"

    def get_eligible_actions(self, user: Combatant, target: Combatant):
        return [a for a in self.static_actions if a.check(user, target)]

# Primarily for use in menus that deal with items
class FakeItem(Item):
    def __init__(
        self,
        base_name: str,
        static_actions: list,
        format_pattern: str = "%s"
    ) -> None:
        self.base_name = base_name
        self.static_actions = static_actions
        self.format_pattern = format_pattern

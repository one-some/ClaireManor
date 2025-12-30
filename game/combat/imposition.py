from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from game.combat.combatant import Combatant, RangedStat
from game import language

class BattleImposition:
    def check(self, combatant: Combatant) -> bool:
        # Check if the requirement can be fufilled
        raise NotImplementedError

    def impose(self, combatant: Combatant) -> None:
        # Take whatever we promised we would
        raise NotImplementedError

    def print(self, combatant: Combatant) -> None:
        raise NotImplementedError

class RangedStatBattleImposition(BattleImposition):
    stat_key = None
    format_pattern = "%s"

    def __init__(self, amount: int) -> None:
        assert(self.stat_key)
        self.amount = amount

    def get_stat(self, combatant: Combatant) -> RangedStat:
        return getattr(combatant, self.stat_key)

    def check(self, combatant: Combatant) -> bool:
        return self.get_stat(combatant).value >= self.amount

    def impose(self, combatant: Combatant) -> None:
        self.get_stat(combatant).alter(-self.amount)

    def format(self, combatant: Combatant) -> None:
        stat = self.get_stat(combatant)
        amount_str = ("+" if self.amount <= 0 else "-") + str(self.amount)
        return language.format(
            f"    [{combatant.lang.pretty_name}] " + self.format_pattern % f"{amount_str} ({stat.value}) {stat.name}",
            combatant=combatant.lang
        )

class StaminaBattleImposition(RangedStatBattleImposition):
    stat_key = "stamina"
    format_pattern = "<darkgreen>%s</darkgreen>"

class HealthBattleImposition(RangedStatBattleImposition):
    stat_key = "health"
    format_pattern = "<red>%s</red>"


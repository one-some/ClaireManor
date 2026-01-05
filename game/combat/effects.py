from __future__ import annotations

import random
import typing
if typing.TYPE_CHECKING:
    from game.combat.combatant import Combatant

from game.combat.imposition import (
    StaminaBattleImposition,
    HealthBattleImposition
)

class StatusEffect:
    name = "Effect"
    turn_impositions = []

    def __init__(self) -> None:
        self.ttl = random.randint(1, 5)

    @classmethod
    async def do_turn(cls, target: Combatant) -> None:
        for r in cls.turn_impositions:
            r.impose(target)
            await print_line(r.format(target))

class BleedingEffect(StatusEffect):
    name = "<red>Bleeding</red>"
    turn_impositions = [HealthBattleImposition(7)]

class ConcussedEffect(StatusEffect):
    # TODO: Skip turn!
    name = "<blue>Concussed</blue>"
    turn_impositions = [StaminaBattleImposition(7)]

class WindedEffect(StatusEffect):
    name = "<darkgreen>Winded</darkgreen>"
    turn_impositions = [StaminaBattleImposition(17)]

class BoredEffect(StatusEffect):
    name = "<darkgreen>Bored...</darkgreen>"
    turn_impositions = [StaminaBattleImposition(17)]

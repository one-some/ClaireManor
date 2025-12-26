from __future__ import annotations

from game import ui
from game import state
from game.ui import print_line

import random
from typing import Optional

class BattleImposition:
    def check(self, combatant: Combatant) -> bool:
        # Check if the requirement can be fufilled
        raise NotImplementedError

    def impose(self, combatant: Combatant) -> None:
        # Take whatever we promised we would
        raise NotImplementedError

class StatBattleImposition(BattleImposition):
    stat = None

    def __init__(self, amount: int) -> None:
        assert(self.stat)
        self.amount = amount

    def check(self, combatant: Combatant) -> bool:
        return getattr(combatant, self.stat).value >= self.amount

    def impose(self, combatant: Combatant) -> None:
        stat = getattr(combatant, self.stat)
        return setattr(stat, "value", stat.value - self.amount)

class StaminaBattleImposition(StatBattleImposition):
    stat = "stamina"

class HealthBattleImposition(StatBattleImposition):
    stat = "health"

class BattleAction:
    def __init__(
        self,
        name: str,
        user_impositions: list[BattleImposition],
        target_impositions: list[BattleImposition],
    ) -> None:
        self.name = name
        self.user_impositions = user_impositions
        self.target_impositions = target_impositions

    def __repr__(self) -> str:
        return self.name

    def check(self, user: Combatant, target: Combatant) -> bool:
        return (
            all([r.check(user) for r in self.user_impositions])
            and
            all([r.check(target) for r in self.target_impositions])
        )

    def execute(self, user: Combatant, target: Combatant) -> None:
        for r in self.user_impositions:
            r.impose(user)

        for r in self.target_impositions:
            r.impose(target)


class Item:
    pass

class Weapon(Item):
    static_actions = []

    def get_eligible_actions(self, user: Combatant, target: Combatant):
        return [a for a in self.static_actions if a.check(user, target)]

class Sword(Weapon):
    static_actions = [
        BattleAction(
            "Slash", 
            user_impositions=[StaminaBattleImposition(4)],
            target_impositions=[HealthBattleImposition(14)],
        )
    ]

class Stat:
    def __init__(self, max_value: float, value: Optional[float] = None) -> None:
        self.max_value = max_value
        self.value = value if value is not None else max_value

    def alter(self, delta: float) -> None:
        self.value += delta
        self.value = max(self.value, 0)
        self.value = min(self.value, self.max_value)

    def __repr__(self):
        return f"<{self.value} / {self.max_value}>"

    def __bool__(self) -> bool:
        return self.value > 0

class Combatant:
    def __init__(self, **kwargs):
        self.name = kwargs.pop("name")

        self.health = Stat(kwargs.pop("max_health"))
        self.stamina = Stat(kwargs.pop("max_stamina"))

        self.items = [Sword()]

        self.target = None

        if kwargs:
            print(kwargs)
            raise RuntimeError("kwargs not exausted")

    def __repr__(self):
        return str(self.__dict__)

class PlayerCombatant(Combatant):
    pass

class EnemyCombatant(Combatant):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.target = state.player_combatant

    def ai_move(self) -> None:
        actions = []

        for item in self.items:
            if isinstance(item, Weapon):
                actions += item.get_eligible_actions(user=self, target=self.target)

        print(actions)

        # TODO: Preference?
        action = random.choice(actions)
        print("Chose", action)
        action.execute(user=self, target=self.target)
        print(self)
        print(self.target)

state.player_combatant = PlayerCombatant(
    name="You",
    max_health=100,
    max_stamina=100,
)

enemy = EnemyCombatant(
    name="Skeleton",
    max_health=100,
    max_stamina=100,
)

enemy.ai_move()

def start_battle():
    ui.switch_active_text_container(ui.battle_text_container)

    print_line("It's time to battle!")

def end_battle():
    ui.switch_active_text_container(ui.story_text_container)

    print_line("Bai")

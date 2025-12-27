from __future__ import annotations

from game import ui
from game import state
from game.ui import print_line

import random
import asyncio
from typing import Optional

class BattleImposition:
    def check(self, combatant: Combatant) -> bool:
        # Check if the requirement can be fufilled
        raise NotImplementedError

    def impose(self, combatant: Combatant) -> None:
        # Take whatever we promised we would
        raise NotImplementedError

class RangedStatBattleImposition(BattleImposition):
    stat = None

    def __init__(self, amount: int) -> None:
        assert(self.stat)
        self.amount = amount

    def check(self, combatant: Combatant) -> bool:
        return getattr(combatant, self.stat).value >= self.amount

    def impose(self, combatant: Combatant) -> None:
        stat = getattr(combatant, self.stat)
        stat.alter(-self.amount)

class StaminaBattleImposition(RangedStatBattleImposition):
    stat = "stamina"

class HealthBattleImposition(RangedStatBattleImposition):
    stat = "health"

class BattleAction:
    name = "Action"
    user_impositions = []
    target_impositions = []
    failure_rate = 0.0

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

        print_line(f"{user.name} slashes {target.name}")

        if random.random() < self.failure_rate:
            print_line("<red>...But it failed!</red>")
            return

        for r in self.target_impositions:
            r.impose(target)


class SlashAction(BattleAction):
    name = "Slash"
    failure_rate = 0.50
    user_impositions = [StaminaBattleImposition(4)]
    target_impositions = [HealthBattleImposition(14)]

class Item:
    pass

class Weapon(Item):
    static_actions = []

    def get_eligible_actions(self, user: Combatant, target: Combatant):
        return [a for a in self.static_actions if a.check(user, target)]

class Sword(Weapon):
    static_actions = [
        SlashAction()
    ]

class RangedStat:
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

        self.health = RangedStat(kwargs.pop("max_health"))
        self.stamina = RangedStat(kwargs.pop("max_stamina"))
        self.speed = kwargs.pop("speed")

        self.items = [Sword()]

        self.target = None

        if kwargs:
            print(kwargs)
            raise RuntimeError("kwargs not exausted")

    def __repr__(self):
        return str(self.__dict__)
    
    async def select_target(self, enemies: list[Combatant]) -> Combatant:
        raise NotImplementedError

    async def do_move(self) -> None:
        raise NotImplementedError

class PlayerCombatant(Combatant):
    async def select_target(self, enemies: list[Combatant]) -> Combatant:
        print_line("Select target:")
        for i, enemy in enumerate(enemies):
            print_line(f"{i + 1}. {enemy.name}")

        range_string = f"1-{len(enemies)}"

        while True:
            number = await ui.prompt(f"[choose a number {range_string}]")
            try:
                num = int(number)
                assert num > 0
                return enemies[int(number) - 1]
            except ValueError:
                print_line(f"Please choose a <red>number</red> {range_string}! Try again.")
            except (AssertionError, IndexError):
                print_line(f"Please choose a number <red>{range_string}</red>! Try again.")

    async def do_move(self) -> None:
        print_line("What will you do? (Use <act>help</act> to see your options!)")
        bebebe = await ui.prompt("Behehe")
        print_line(bebebe)


class EnemyCombatant(Combatant):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    async def select_target(self, enemies: list[Combatant]) -> Combatant:
        return random.choice(enemies)

    async def do_move(self) -> None:
        actions = []

        for item in self.items:
            if isinstance(item, Weapon):
                actions += item.get_eligible_actions(user=self, target=self.target)

        print(actions)

        # TODO: Preference?
        action = random.choice(actions)
        action.execute(user=self, target=self.target)
        await asyncio.sleep(2.0)

class Battle:
    def __init__(self, parties: list[list[Combatant]]) -> None:
        self.parties = parties
        # Infamous "two-party system"
        assert len(self.parties) == 2

    async def do_turn(self) -> None:
        everyone = []

        for party in self.parties:
            everyone += party

        # Mix it up because python sort is stable
        random.shuffle(everyone)
        everyone.sort(key=lambda x: x.speed, reverse=True)

        for combatant in everyone:
            enemies = []
            for party in self.parties:
                if combatant in party:
                    continue
                enemies += party

            combatant.target = await combatant.select_target(enemies)
            await combatant.do_move()


async def battle_loop():
    ui.switch_active_text_container(ui.battle_text_container)

    battle = Battle([
        [
            PlayerCombatant(
                name="You",
                max_health=100,
                max_stamina=100,
                speed=15,
            ),
        ],
        [
            EnemyCombatant(
                name="Skeleton",
                max_health=100,
                max_stamina=100,
                speed=random.randint(1, 30)
            ),
            EnemyCombatant(
                name="Silly Skeleton",
                max_health=100,
                max_stamina=100,
                speed=random.randint(1, 30)
            ),
            EnemyCombatant(
                name="Genius Skeleton",
                max_health=100,
                max_stamina=100,
                speed=random.randint(1, 30)
            ),
        ]
    ])

    while True:
        await battle.do_turn()

    print_line("It's time to battle!")

def end_battle():
    ui.switch_active_text_container(ui.story_text_container)

    print_line("Bai")

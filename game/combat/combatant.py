from __future__ import annotations

import random
import asyncio
from typing import Optional
from game.io import print_line, choice_prompt
from game.items.item import Item, FakeItem
from game.items.weapon import Weapon
from game.combat.action import BattleAction, PunchAction

class RangedStat:
    def __init__(self, name: str, max_value: float, value: Optional[float] = None) -> None:
        self.name = name
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
    base_actions = []
    def __init__(self, **kwargs):
        self.lang = kwargs.pop("lang")

        self.health = RangedStat("Health", kwargs.pop("max_health"))
        self.stamina = RangedStat("Stamina", kwargs.pop("max_stamina"))
        self.speed = kwargs.pop("speed")

        self.inventory = kwargs.pop("inventory")

        if kwargs:
            print(kwargs)
            raise RuntimeError("kwargs not exausted")

    def __repr__(self) -> str:
        return str(self.__dict__)
    
    async def plan_attack(self, enemies: list[Combatant]) -> (Optional[BattleAction], Optional[Combatant]):
        raise NotImplementedError

    async def do_move(self, action: BattleAction, target: Combatant) -> None:
        await action.execute(user=self, target=target)
        await asyncio.sleep(0.5)

class PlayerCombatant(Combatant):
    base_actions = [
        PunchAction()
    ]

    async def choose_target(self, enemies: list[Combatant]) -> Combatant:
        targets = [self] + enemies
        return await choice_prompt(
            "Who will you target?",
            {target.lang.pretty_name: target for target in targets}
        )

    async def choose_item_action(self, item: Item) -> Optional[BattleAction]:
        return await choice_prompt(
            f"What will you do with {item.name}?",
            {action.name: action for action in item.static_actions},
            include_back=True
        )

    async def choose_root_action(self) -> Optional[BattleAction]:
        flesh_and_bone = FakeItem(
            "Flesh and Bone",
            self.base_actions,
            format_pattern="<darkred>%s</darkred>"
        )

        options = {
            **{weapon.list_formatted: weapon for weapon in self.inventory.weapons + [flesh_and_bone]},
            "<blue>Items</blue>": "ITEMS",
            "<gray>Skip Turn</gray>": "SKIP",
        }

        while True:
            choice = await choice_prompt("What will you use?", options)

            if choice == "SKIP":
                return None

            if isinstance(choice, Item):
                action = await self.choose_item_action(choice)
                print("Chose", action)
                if not action:
                    continue
                return action

            if choice == "ITEMS":
                while True:
                    inv_item = await choice_prompt(
                        "Which item will you use?",
                        {item.list_formatted: item for item in self.inventory.non_weapons},
                        include_back=True
                    )

                    if not inv_item:
                        break

                    action = await self.choose_item_action(inv_item)

                    if not action:
                        continue

                    return action
                continue
            
            assert False

    async def plan_attack(self, enemies: list[Combatant]) -> (Optional[BattleAction], Optional[Combatant]):
        # TODO: Press just enter to do default (last). Remember to invalidate! :3
        await print_line(" ")

        action = await self.choose_root_action()

        if not action:
            return None, None

        # Get target
        target = await self.choose_target(enemies)

        return action, target

# TODO: Subclass for enemy types
class EnemyCombatant(Combatant):
    base_actions = [
        PunchAction()
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    async def plan_attack(self, enemies: list[Combatant]) -> (Optional[BattleAction], Optional[Combatant]):
        target = random.choice(enemies)

        actions = []
        for item in self.inventory:
            if isinstance(item, Weapon):
                actions += item.get_eligible_actions(user=self, target=target)

        # TODO: Preference?
        action = random.choice(actions)

        return action, target


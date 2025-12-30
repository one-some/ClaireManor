from __future__ import annotations

import random
import asyncio
from typing import Optional

from game import io
from game.io import print_line, choice_prompt

from game import ui
from game import state
from game import language
from game.language import PronounSet, LanguageProfile, MessagePool

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

class BattleAction:
    name = "Action"
    user_impositions = []
    target_impositions = []
    fail_rate = 0.0

    attempt_messages = ["A try was made"]
    fail_messages = ["...But it failed!"]

    def __repr__(self) -> str:
        return self.name

    def check(self, user: Combatant, target: Combatant) -> bool:
        return (
            all([r.check(user) for r in self.user_impositions])
            and
            all([r.check(target) for r in self.target_impositions])
        )

    async def execute(self, user: Combatant, target: Combatant) -> None:
        await print_line(
            language.format(
                self.attempt_messages.sample(),
                user=user.lang,
                target=target.lang,
                # TODO: SAVE SELF LANG
                # weapon=LanguageProfile(self.name, PronounSet.IT)
            )
        )

        for r in self.user_impositions:
            r.impose(user)
            await print_line(r.format(user))

        if random.random() < self.fail_rate:
            message = language.format(
                self.fail_messages.sample(),
                user=user.lang,
                target=target.lang,
            )

            await print_line(f"<red>{message}</red>")
            return

        for r in self.target_impositions:
            r.impose(target)
            await print_line(r.format(target))


class SlashAction(BattleAction):
    name = "Slash"
    user_impositions = [StaminaBattleImposition(4)]
    target_impositions = [HealthBattleImposition(14)]
    fail_rate = 0.20

    attempt_messages = MessagePool([
        # "{User} slashes {Target} with {user.his} {Weapon}"
        "{User} slashes {Target}"
    ])

    fail_messages = MessagePool([
        "{User} {user.misses} {Target}!",
        "{Target} {target.evades} {User's} slash!",
        "{User} can't seem to hit {Target}!",
        "{Target} {target.is} too fast for {User}!",
        "{Target} {target.dodges} {User's} slash!",
        "{Target} {target.manages} to escape {User's} slash!",
    ])

class StabAction(BattleAction):
    name = "Stab"
    user_impositions = [StaminaBattleImposition(15)]
    target_impositions = [HealthBattleImposition(20)]
    # TODO: BLEEDING
    fail_rate = 0.50

    attempt_messages = MessagePool([
        # "{User} stabs at {Target} with {user.his} {Weapon}"
        "{User} {user.stabs} at {Target}"
    ])

    fail_messages = MessagePool([
        "{User} {user.misses} {Target}!",
        "{User} can't seem to hit {Target}!",
        "{Target} {target.is} too fast for {User}!",
    ])

class PunchAction(BattleAction):
    name = "Punch"
    user_impositions = [StaminaBattleImposition(17)]
    target_impositions = [HealthBattleImposition(5)]
    fail_rate = 0.20

    attempt_messages = MessagePool([
        "{User} {user.swings} at {Target}"
    ])

    fail_messages = MessagePool([
        "{User} {user.misses} {Target}!",
        "{User} can't seem to hit {Target}!",
        "{Target} {target.is} too fast for {User}!",
    ])

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

class Weapon(Item):
    base_name = "Unknown Weapon"
    format_pattern = "<green>%s</green>"

class Dagger(Weapon):
    base_name = "Dagger"

    static_actions = [
        SlashAction(),
        StabAction()
    ]

class Sword(Weapon):
    base_name = "Sword"

    static_actions = [
        SlashAction()
    ]

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

        self.items = [Sword(), Dagger()]

        if kwargs:
            print(kwargs)
            raise RuntimeError("kwargs not exausted")

    @property
    def weapons(self) -> list[Weapon]:
        return [item for item in self.items if isinstance(item, Weapon)]

    @property
    def weapons(self) -> list[Weapon]:
        return [item for item in self.items if isinstance(item, Weapon)]

    @property
    def non_weapons(self) -> list[Weapon]:
        # Ooookay this is a litttttle weird
        return [item for item in self.items if not isinstance(item, Weapon)]

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
            **{weapon.list_formatted: weapon for weapon in self.weapons + [flesh_and_bone]},
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
                        {item.list_formatted: item for item in self.non_weapons},
                        include_back=True
                    )

                    if not inv_item:
                        break

                    action = await self.choose_action(inv_item)

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
        for item in self.items:
            if isinstance(item, Weapon):
                actions += item.get_eligible_actions(user=self, target=target)

        # TODO: Preference?
        action = random.choice(actions)

        return action, target

class Battle:
    join_messages = MessagePool([
        "{Guy} {guy.joins} the battle!",
        "{Guy} {guy.appears} out of nowhere!",
        "You're approached by {Guy}!",
    ])

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

            action, target = await combatant.plan_attack(enemies)
            if action and target:
                await print_line("---")
                await combatant.do_move(action, target)

    async def update_parties(self, new_members: list[list[Combatant]]) -> None:
        # There's probably a way to not have to iterate over the parties in
        # various ways 4 times
        new_combatants = []
        assert len(new_members) == 2
        for i, party in enumerate(new_members):
            self.parties[i] += party
            new_combatants += party

        # Format [Skeleton, Skeleton] as [Skeleton (1), Skeleton (2)]
        # TODO: Could we instead distribute random attributes that are
        # pointless but differentiate?
        names = {}
        for party in self.parties:
            for combatant in party:
                name = combatant.lang.true_name

                if name not in names:
                    names[name] = []

                names[name].append(combatant.lang)

        for name, langs in names.items():
            if len(langs) < 2:
                continue

            for i, lang in enumerate(langs):
                lang.display_name = f"{name} ({i + 1})"

        # This must happen after names are fixed
        for combatant in new_combatants:
            await print_line(language.format(
                Battle.join_messages.sample(),
                guy=combatant.lang
            ))

def conjure_enemies() -> list[EnemyCombatant]:
    out = []

    for i in range(3):
        out.append(EnemyCombatant(
            lang=LanguageProfile("Skeleton", PronounSet.IT, "<gray>%s</gray>"),
            max_health=100,
            max_stamina=100,
            speed=random.randint(1, 30)
        ))

    return out

async def battle_loop():
    ui.switch_active_text_container(ui.battle_text_container)

    pc = PlayerCombatant(
        lang=LanguageProfile("You", PronounSet.YOU, "<gold>%s</gold>"),
        max_health=100,
        max_stamina=100,
        speed=15,
    )

    battle = Battle([[pc], []])

    await print_line("=== It's time to battle! ===")
    await battle.update_parties([[], conjure_enemies()])

    await asyncio.sleep(1.0)

    while True:
        await battle.do_turn()

        # DEBUG
        await asyncio.sleep(0.0)

    await print_line("Bai")
    ui.switch_active_text_container(ui.story_text_container)

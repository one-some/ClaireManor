from __future__ import annotations

from game import ui
from game import state
from game import language
from game.ui import print_line
from game.language import PronounSet, LanguageProfile, MessagePool

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
        "{User} stabs at {Target}"
    ])

    fail_messages = MessagePool([
        "{User} {user.misses} {Target}!",
        "{User} can't seem to hit {Target}!",
        "{Target} {target.is} too fast for {User}!",
    ])

class Item:
    pass

class Weapon(Item):
    static_actions = []

    def get_eligible_actions(self, user: Combatant, target: Combatant):
        return [a for a in self.static_actions if a.check(user, target)]

class Dagger(Weapon):
    static_actions = [
        SlashAction(),
        StabAction()
    ]

class Sword(Weapon):
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
    def __init__(self, **kwargs):
        self.lang = kwargs.pop("lang")

        self.health = RangedStat("Health", kwargs.pop("max_health"))
        self.stamina = RangedStat("Stamina", kwargs.pop("max_stamina"))
        self.speed = kwargs.pop("speed")

        self.items = [Sword(), Dagger()]

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
        await print_line("Select target:")
        for i, enemy in enumerate(enemies):
            await print_line(f"{i + 1}. {enemy.lang.pretty_name}")

        range_string = f"1-{len(enemies)}"

        while True:
            number = await ui.prompt(f"[choose a number {range_string}]")
            try:
                num = int(number)
                assert num > 0
                return enemies[int(number) - 1]
            except ValueError:
                await print_line(f"Please choose a <red>number</red> {range_string}! Try again.")
            except (AssertionError, IndexError):
                await print_line(f"Please choose a number <red>{range_string}</red>! Try again.")

    async def do_move(self) -> None:
        await print_line("What will you do? (Use <act>help</act> to see your options!)")
        bebebe = await ui.prompt("Behehe")
        await print_line(bebebe)


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
        await action.execute(user=self, target=self.target)
        await asyncio.sleep(2.0)

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

            combatant.target = await combatant.select_target(enemies)

            await print_line(" ")
            await combatant.do_move()

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

    await print_line("Bai")
    ui.switch_active_text_container(ui.story_text_container)

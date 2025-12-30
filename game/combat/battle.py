from __future__ import annotations

import random
import asyncio
from typing import Optional

from game import io
from game.io import print_line, choice_prompt

from game import ui
from game import state
from game import language
from game.player import Player
from game.language import PronounSet, LanguageProfile, MessagePool
from game.items.inventory import Inventory
from game.items.weapon import Sword
from game.combat.combatant import Combatant, PlayerCombatant, EnemyCombatant

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
        names: dict[str, list[LanguageProfile]] = {}
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
            speed=random.randint(1, 30),
            inventory=Inventory([Sword()])
        ))

    return out

async def battle_loop():
    ui.switch_active_text_container(ui.battle_text_container)

    battle = Battle([[Player.player.combatant], []])

    await print_line("=== It's time to battle! ===")
    await battle.update_parties([[], conjure_enemies()])

    await asyncio.sleep(1.0)

    while True:
        await battle.do_turn()

        # DEBUG
        await asyncio.sleep(0.0)

    await print_line("Bai")
    ui.switch_active_text_container(ui.story_text_container)

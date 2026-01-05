from __future__ import annotations

import random
import asyncio
from typing import Optional

from game import io
from game.io import print_line, choice_prompt, wait_for_enter

from game import ui
from game import language
from game.language import PronounSet, LanguageProfile, MessagePool
from game.items.inventory import Inventory
from game.items.weapon import Sword
from game.combat.combatant import (
    Combatant,
    PlayerCombatant,
    EnemyCombatant,
    EnemyAppearance,
    LetMeOutException,
)

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

    def is_party_dead(self, party: list) -> None:
        return all([not c.is_alive for c in party])

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

            # If a whole party is dead, stop the show
            for party in self.parties:
                if self.is_party_dead(party):
                    print("Ded2")
                    raise LetMeOutException

        for party in self.parties:
            if self.is_party_dead(party):
                print("Ded1")
                raise LetMeOutException

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

def conjure_enemies(enemy_pool: list[EnemyAppearance]) -> list[EnemyCombatant]:
    out = []

    # TODO: Scale with player level!!!
    enemy_amount = random.randint(1, 3)

    appearances = random.choices(
        population=enemy_pool,
        weights=[a.weight for a in enemy_pool],
        k=enemy_amount
    )

    for appearance in appearances:
        out.append(appearance.combatant(
            max_health=100,
            max_stamina=100,
            speed=random.randint(1, 30),
            inventory=Inventory([Sword()])
        ))

    return out

async def battle_loop(player: Player, enemy_pool: list[EnemyAppearance]):
    ui.switch_active_text_container(ui.battle_text_container)

    battle = Battle([[player.combatant], []])
    await print_line("=== It's time to battle! ===")

    await battle.update_parties([[], conjure_enemies(enemy_pool)])

    # Not a fan of the death detection code....
    player_party = battle.parties[0]
    enemy_party = battle.parties[1]

    await asyncio.sleep(1.0)

    while True:
        try:
            await battle.do_turn()
        except LetMeOutException:
            break

        # DEBUG
        await asyncio.sleep(0.0)

    ui.switch_active_text_container(ui.story_text_container)
    await print_line("The battle is over!")
    await wait_for_enter()

    if battle.is_party_dead(player_party):
        await print_line("You die!")
        await player.on_die()
    elif battle.is_party_dead(enemy_party):
        await print_line("You have vanquished your enemies!")

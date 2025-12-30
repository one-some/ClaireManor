from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    # I think this is maybe the worst thing about Python typing
    # ...alongside it not being enforced. I hate the Python
    # module system with a fervor unseen before on this earth
    from game.combat.combatant import Combatant

import random
from game.combat.imposition import (
    StaminaBattleImposition,
    HealthBattleImposition
)
from game import language
from game.language import PronounSet, LanguageProfile, MessagePool
from game.io import print_line

class BattleAction:
    name = "Action"
    user_impositions = []
    target_impositions = []
    fail_rate = 0.0

    attempt_messages = MessagePool(["A try was made"])
    fail_messages = MessagePool(["...But it failed!"])

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

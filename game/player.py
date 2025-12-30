from __future__ import annotations

from game.language import LanguageProfile, PronounSet
from game.items.inventory import Inventory
from game.combat.combatant import PlayerCombatant

class Player:
    player: Player

    def __init__(self) -> None:
        self.lang = LanguageProfile("You", PronounSet.YOU, "<gold>%s</gold>")
        self.inventory = Inventory([])

        self.combatant = PlayerCombatant(
            lang=self.lang,
            max_health=100,
            max_stamina=100,
            speed=15,
            inventory=self.inventory
        )

Player.player = Player()

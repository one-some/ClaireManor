from __future__ import annotations

import random
import pickle
import asyncio
from pathlib import Path

from game import fs
from game import ui
from game.combat import battle
from game.items.inventory import Inventory
from game.items.weapon import SilverDagger
from game.io import print_line, wait_for_enter, clear_lines
from game.combat.combatant import PlayerCombatant
from game.location import EntrywayLocation
from game.language import LanguageProfile, PronounSet, MessagePool

class Player:
    SAVE_PATH = fs.SAVE_DIR / "plr001.save"

    player: Player
    watched_msg = MessagePool([
        "Your hair stands up on end...",
        "You feel watched...",
        "A chill runs down your spine...",
        "The room is eerily silent...",
    ])
    
    def __init__(self) -> None:
        self.lang = LanguageProfile("You", PronounSet.YOU, "<gold>%s</gold>")
        self.inventory = Inventory([
            SilverDagger()
        ])

        self.location = EntrywayLocation

        self.danger = 0

        self.combatant = PlayerCombatant(
            lang=self.lang,
            max_health=100,
            max_stamina=100,
            speed=15,
            inventory=self.inventory
        )

    @staticmethod
    def load(path: str) -> Player:
        # NOTE: This is the wimpy way out. In future make a to_json chain maybe
        with open(path, "rb") as file:
            return pickle.load(file)

    def save(self) -> None:
        with open(self.SAVE_PATH, "wb") as file:
            return pickle.dump(self, file)

    async def set_location(self, location: Location) -> None:
        # Setters can't be async
        self.location = location

        ui.change_background(location.name.lower().replace(" ", "_"))

    async def post_location_change(self, location: Location) -> None:
        # Split so we don't wait for the printing in the loading screen
        await location.describe()

        self.danger += random.random() * 0.4

        if self.danger > 0.7:
            line = self.watched_msg.sample()
            await print_line(f"<darkred>{line}</darkred>")

        if self.danger >= 1.0 and location.enemy_pool:
            self.danger = 0.0
            await print_line(f"<red>Enemies jump out from the shadows!</red>")
            await wait_for_enter()
            await battle.battle_loop(self, location.enemy_pool)

        # self.save()

    async def on_die(self) -> None:
        await print_line("You have died! Will you wake up? Was it all a dream?")
        await wait_for_enter()

        clear_lines()
        self.load(self.SAVE_PATH)
        await self.location.describe()

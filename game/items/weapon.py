from game.items.item import Item
from etc.utils import get_subclasses
from game.combat.action import StabAction, SlashAction, BashAction

class Weapon(Item):
    base_name = "Unknown Weapon"
    format_pattern = "<green>%s</green>"

    @staticmethod
    def get_weapons() -> list[type]:
        return get_subclasses(Weapon)

class Dagger(Weapon):
    base_name = "Dagger"

    static_actions = [
        SlashAction(),
        StabAction()
    ]

class SilverDagger(Dagger):
    base_name = "Silver Dagger"

class Club(Weapon):
    base_name = "Club"

    static_actions = [
        BashAction(),
    ]

class BoneClub(Club):
    base_name = "Bone Club"

class Sword(Weapon):
    base_name = "Sword"

    static_actions = [
        SlashAction()
    ]

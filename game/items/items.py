from game.items.item import Item

class LeatherCoat(Item):
    base_name = "Leather Coat"
    description = "An old leather coat. It's dusty from disuse. I won't touch it, out of respect."

class TragedyMask(Item):
    # This was supposed to be a multiplayer battle mechanic, but I ran out of time!
    base_name = "Tragedy Mask"
    description = "An old, crumbling mask. It looks like one of the tragedy masks from ancient theatre."

class ComedyMask(Item):
    base_name = "Comedy Mask"
    description = "An old, crumbling mask. It looks like one of the comedy masks from ancient theatre."

class DarcyNote(Item):
    base_name = "Darcy's Note"
    description = "A ruined fragment of an old message, written in a flowery script. <claire>You recognize this handwriting.</claire>"
    details = (
        "\"Miss Darcy: You'll have to excuse me for my behavior earlier tonight. As I get older " \
        "I find myself somehow more sensitive around topics I should be long-numb to. I would " \
        "love to make up for the trouble somehow. Meet me in my boudoir after the procession " \
        "concludes tonight. I have something to show you. Not once in my life did I\" " \
        "\n... The rest is indecipherable."
    )


class EvilYarn(Item):
    base_name = "Yarn Scrap"
    description = "A short scrap of red yarn. It's obviously yarn, but its texture feels almost abrasive."

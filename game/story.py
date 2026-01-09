import asyncio

from game.ui import (
    ui_root,
    input_box,
    ui_process,
    Fade
)
from game.io import print_line, prompt, clear_lines
from game.dialog import add_dialog, print_dialog

# Populated by decorators
cutscenes = {}

async def play_cutscene(name: str) -> None:
    # So we don't have to import all that nonsense...

    # Originally this was done with decorators but this makes more sense imo
    coroutine = globals()[f"cutscene_{name}"]
    assert coroutine

    await coroutine()

async def cutscene_intro() -> None:
    Fade.set_overlay_alpha(1.0)
    await Fade(0.0).wait_for()

    await print_dialog(". . .")
    await print_dialog("Your eyes gradually open to the sound of hooves clacking on cobblestone. You must've drifted off on your journey. It has been a long one, after all.")
    await add_dialog("Coachman", "Not much longer, I reckon.")
    await print_dialog("The voice of the <gray>Coachman</gray> startles you. You do not immediately respond.")
    await add_dialog("Coachman", "Yer a weird fella, you know? Not many folks come out this far.")
    await print_dialog("The moonlight illuminates his suspicion-wraught features. Your lips purse.")
    await add_dialog("You", "Why take the drive if you don't trust me to pay?")
    await print_dialog("He chuckles and waves his hand in dismissal.")
    await add_dialog("Coachman", "Naw, naw. That ain't what I mean...")

    await print_dialog("...")
    await print_dialog("An awkward pause fills the air.")

    await add_dialog("Coachman", "The house, kid. You think I don't know?")
    await add_dialog("Coachman", "Every couple years something comes up about it. Someone goes missing and somehow it's that damn house's fault.")
    await add_dialog("Coachman", "Everyone wants to be an adventurer nowadays...")

    await print_dialog("The <gray>Coachman</gray> looks you in the eyes with a dubious squint.")

    await add_dialog("You", "I'm no adventurer. I'm here to visit <claire>Lady Claire</claire>.")
    await print_dialog("You pull from your satchel a bronze key dangling from a string. The <gray>Coachman</gray>'s lips widen into a smile and he lets out a hearty chuckle.")

    await add_dialog("Coachman", "Ho-ho! And I thought the <claire>Lady</claire> was old when I was a scrap!")

    await print_dialog("The <gray>Coachman</gray> suddenly pulls back the reins and the carriage comes to a halt. Looking up, you notice the manor has appeared before you.")
    await add_dialog("Coachman", "Look, kid, it ain't my job to sit here and tell you what you can or can't do. Just keep me out of it.")

    await print_dialog("You hand over a small pouch of coins, and the <gray>Coachman</gray> starts to ride away, grumbling something about the <claire>Lady</claire>.")

    await print_dialog("...")

    await print_dialog("You walk up the steps to the manor and insert your key. With some resistance, it turns int he lock and the front door swings open.")
    await print_dialog(" ")
    await print_dialog("You cross the threshold into the Manor Claire.")

    await Fade(1.0).wait_for()


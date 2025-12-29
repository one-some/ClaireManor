from __future__ import annotations

import pyray as rl
from ui.text import RichText, RichTextChunk

print("\nTake a look!\n")

# The window needs to be initalized before about anything can happen
# without segfaults
rl.set_trace_log_level(rl.TraceLogLevel.LOG_WARNING)
rl.set_window_state(rl.ConfigFlags.FLAG_WINDOW_RESIZABLE | rl.ConfigFlags.FLAG_WINDOW_HIGHDPI)
rl.init_window(800, 450, "The Manor Claire")
rl.set_target_fps(60)

import sys
import font
import asyncio
from game.cmd import run_command
from ui.vector2 import Vector2
from ui.renderable import Renderable
from game import ui
from game import battle
from game.ui import (
    ui_root,
    print_line,
    input_box,
    ui_process,
    enter_to_continue,
    prompt,
    add_dialog,
    print_dialog,
    Fade
)

# Font loading has to be done after the rl context is initalized. Pretty hacky
# but whatevs...
Renderable.font = font.load_jagged_ttf("static/unscii-16.ttf", 16);
render_scale = rl.get_screen_height() / 720
Renderable.font_size = round(Renderable.font.baseSize / render_scale / 16) * 16

# HACK: Set input_box's static size to it's measurement to prevent weird sizing
# HACK: Also has to be down here because of delayed font loading :(
input_box.static_size = input_box.measure()
ui.battle_stats.static_size = ui.battle_stats.measure()
input_box.on_submit = run_command

def main_menu():
    print_line(RichText([
        RichTextChunk("Welcome to "),
        RichTextChunk("The Manor Claire", color=rl.BEIGE),
        RichTextChunk("."),
    ]))
    print_line("This is a text-based game with some visuals for atmosphere, made for CSC 1313.")
    print_line("It's a little over-engineered and has some cool features. Check out README.md for more information.")
    print_line("The UI is reactive, so feel free to resize. You can also fullscreen with F11.")
    print_line("")
    print_line(RichText([
        RichTextChunk("Would you like to "),
        RichTextChunk("play", color=rl.ORANGE),
        RichTextChunk("? Perhaps "),
        RichTextChunk("load", color=rl.ORANGE),
        RichTextChunk(" an existing save file? Or maybe join a "),
        RichTextChunk("multiplayer", color=rl.ORANGE),
        RichTextChunk(" lobby?"),
    ]))

async def intro():
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
    ui.clear_lines()
    await asyncio.sleep(1.0)
    await Fade(0.0).wait_for()


    # print_line("You shake yourself awake and sit up. You must decide how to proceed. Perhaps start by <act>look</act>ing around.")
    # await battle.battle_loop()

    # print_line("nevermind. Here comes to Monster.")
    # await enter_to_continue()
    # print_line("Nope. Wait, what was your name again?")
    # name = await prompt("name?")
    # print_line(f"Oh, hi {name}")

async def render_and_process():
    while not rl.window_should_close():
        if rl.is_key_pressed(rl.KEY_F11):
            rl.toggle_borderless_windowed()

        ui_process()

        ui_root.reflow_layout(Vector2(
            rl.get_render_width(),
            rl.get_render_height()
        ))

        rl.begin_drawing()
        rl.clear_background(rl.BLACK)

        ui_root.render(Vector2.zero())

        rl.end_drawing()

        # Yield
        await asyncio.sleep(0)

    rl.close_window()
    sys.exit(0)

async def story():
    await intro()

async def main():
    try:
        await asyncio.gather(
            story(),
            render_and_process()
        )
    except SystemExit:
        # A little questionable...
        pass

asyncio.run(main())

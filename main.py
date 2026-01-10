from __future__ import annotations

import sys
import pyray as rl
import asyncio

print("\nTake a look!\n")

# The window needs to be initalized before about anything can happen
# without segfaults
rl.set_trace_log_level(rl.TraceLogLevel.LOG_WARNING)
rl.set_window_state(rl.ConfigFlags.FLAG_WINDOW_RESIZABLE | rl.ConfigFlags.FLAG_WINDOW_HIGHDPI)
rl.init_window(800, 450, "The Manor Claire")
rl.init_audio_device()
rl.set_target_fps(60)

from ui.vector2 import Vector2
from ui.renderable import Renderable
from ui.container import HStackContainer, HAlign
from ui.image import ImageRenderable

from etc import font
from game import ui
from game import sfx
from game import story
from game.io import prompt, choice_prompt, print_line, clear_lines
from game.cmd import run_command
from game.combat import battle
from game.dialog import print_dialog
from game.player import Player
from game.ui import Fade

# Font loading has to be done after the rl context is initalized. Pretty hacky
# but whatevs...
Renderable.font = font.load_jagged_ttf("static/unscii-16.ttf", 16);
render_scale = rl.get_screen_height() / 720
Renderable.font_size = round(Renderable.font.baseSize / render_scale / 16) * 16

# HACK: Set input_box's static size to it's measurement to prevent weird sizing
# HACK: Also has to be down here because of delayed font loading :(
ui.input_box.static_size = ui.input_box.measure()
ui.battle_stats.static_size = ui.battle_stats.measure()


async def render_and_process() -> None:
    while not rl.window_should_close():
        if rl.is_key_pressed(rl.KEY_F11):
            rl.toggle_borderless_windowed()

        ui.ui_process()
        sfx.music_loop_tick()

        ui.ui_root.reflow_layout(Vector2(
            rl.get_render_width(),
            rl.get_render_height()
        ))

        rl.begin_drawing()
        rl.clear_background(rl.BLACK)

        ui.ui_root.render(Vector2.zero())

        rl.end_drawing()

        # Yield
        await asyncio.sleep(0)

    rl.close_window()
    sys.exit(0)

async def main_menu() -> None:
    if "--continue" in sys.argv:
        return "CONTINUE"

    Fade.set_overlay_alpha(1.0)
    center_cont = HStackContainer(
        h_align=HAlign.CENTER,
        parent=ui.active_text_container,
        padding=Vector2(0, 500)
    )
    ImageRenderable("static/ui/title.png", parent=center_cont, scale=3.0)
    ui.change_background("menu")

    await Fade(0.0).wait_for()

    await print_dialog("<white>Welcome to <claire>The Manor Claire</claire>.</white>", wait=False)
    await asyncio.sleep(0.3)
    await print_dialog(
        "This game was written by <yellow>McCown</yellow> with story help and music by <yellow>Grantham</yellow>.",
        wait=False
    )

    await asyncio.sleep(0.3)
    await print_dialog(
        "Special thanks to <yellow>raylib</yellow> and the <yellow>pyray</yellow> binding for it.",
        wait=False
    )

    await asyncio.sleep(0.3)
    await print_dialog("The game is incomplete. Check out README.md for more info!", wait=False)
    await asyncio.sleep(0.3)
    await print_line(" ")

    options = {
        "<paleblue>Start Anew</paleblue>": "NEWGAME",
        "<darkred>Chicken Out To Desktop</darkred>": "QUIT",
    }

    if Player.SAVE_PATH.is_file():
        options = {"<palegreen>Continue Your Adventure</palegreen>": "CONTINUE"} | options

    choice = await choice_prompt(f"What would you like to do?", options)

    await Fade(1.0, speed=0.05).wait_for()
    clear_lines()
    return choice

async def linear() -> None:
    menu_choice = await main_menu()
    if menu_choice == "QUIT":
        sys.exit(0)
        return

    if menu_choice == "NEWGAME":
        Player.player = Player()
        Player.player.save()
        await story.play_cutscene("intro")
    elif menu_choice == "CONTINUE":
        Player.player = Player.load(Player.SAVE_PATH)

    clear_lines()
    await Fade(0.0, speed=0.02).wait_for()
    await Player.player.set_location(Player.player.location)
    await Player.player.location.describe()

    while True:
        command_line = await prompt("[cmd]")
        await run_command(command_line)

async def main() -> None:
    try:
        await asyncio.gather(
            linear(),
            render_and_process()
        )
    except SystemExit:
        # A little questionable...
        pass

asyncio.run(main())

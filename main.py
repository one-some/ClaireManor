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
rl.set_target_fps(60)

import font
from game.cmd import run_command
from ui.vector2 import Vector2
from ui.renderable import Renderable
from ui.text import RichText, RichTextChunk
from game.io import prompt
from game import ui
from game import battle
from game import story

# Font loading has to be done after the rl context is initalized. Pretty hacky
# but whatevs...
Renderable.font = font.load_jagged_ttf("static/unscii-16.ttf", 16);
render_scale = rl.get_screen_height() / 720
Renderable.font_size = round(Renderable.font.baseSize / render_scale / 16) * 16

# HACK: Set input_box's static size to it's measurement to prevent weird sizing
# HACK: Also has to be down here because of delayed font loading :(
ui.input_box.static_size = ui.input_box.measure()
ui.battle_stats.static_size = ui.battle_stats.measure()


async def render_and_process():
    while not rl.window_should_close():
        if rl.is_key_pressed(rl.KEY_F11):
            rl.toggle_borderless_windowed()

        ui.ui_process()

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

async def linear():
    # await battle.battle_loop()
    # await story.play_cutscene("intro")

    while True:
        print(ui.input_box)
        command_line = await prompt("[cmd]")
        await run_command(command_line)

async def main():
    try:
        await asyncio.gather(
            linear(),
            render_and_process()
        )
    except SystemExit:
        # A little questionable...
        pass

asyncio.run(main())

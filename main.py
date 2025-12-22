from __future__ import annotations

import pyray as rl

import font
from ui.vector2 import Vector2
from ui.renderable import Renderable
from game.ui import ui_root, print_line, input_box

# TODO:

rl.set_trace_log_level(rl.TraceLogLevel.LOG_WARNING)
rl.init_window(800, 450, "The Manor Claire")
rl.set_window_state(rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)

# Font loading has to be done after the rl context is initalized. Pretty hacky
# but whatevs...
Renderable.font = font.load_jagged_ttf("static/unscii-16.ttf", 16);

# HACK: Set input_box's static size to it's measurement to prevent weird sizing
# HACK: Also has to be down here because of delayed font loading :(
input_box.static_size = input_box.measure()

print_line("Welcome to The Manor Claire.")
print_line("Say 'help' or '?' at any time for a guide on how to play the game.")

while not rl.window_should_close():
    ui_root.reflow_layout(Vector2(
        rl.get_render_width(),
        rl.get_render_height()
    ))

    rl.begin_drawing()
    rl.clear_background(rl.BLACK)

    ui_root.render()

    rl.end_drawing()
rl.close_window()

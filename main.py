from __future__ import annotations

import pyray as rl
from ui.text import RichText, RichTextChunk

# The window needs to be initalized before about anything can happen
# without segfaults
rl.set_trace_log_level(rl.TraceLogLevel.LOG_WARNING)
rl.init_window(800, 450, "The Manor Claire")
rl.set_target_fps(60)
rl.set_window_state(rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)

import font
from game.cmd import run_command
from ui.vector2 import Vector2
from ui.renderable import Renderable
from game.ui import ui_root, print_line, input_box, ui_process

# TODO:

# Font loading has to be done after the rl context is initalized. Pretty hacky
# but whatevs...
Renderable.font = font.load_jagged_ttf("static/unscii-16.ttf", 16);

# HACK: Set input_box's static size to it's measurement to prevent weird sizing
# HACK: Also has to be down here because of delayed font loading :(
input_box.static_size = input_box.measure()
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

def intro():
    print_line(". . .")
    print_line(
        "You awaken on a dusty couch in the middle of an antiquated sitting " \
        "room. The world around you is dimly illuminated, flickering in and " \
        "out to the irregular cadence of the fireplace before you. The " \
        "fireplace is lit, but dying. Without it you wont be able to see " \
        "much of anything."
    )
    print_line(" ")

    print_line("You shake yourself awake and sit up. You must decide how to proceed. Perhaps start by <act>look</act>ing around.")

intro()
# print_line("Say 'help' or '?' at any time for a guide on how to play the game.")

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

    ui_root.render()

    rl.end_drawing()
rl.close_window()

import pyray as rl

from ui.vector2 import Vector2
from ui.renderable import Renderable, EmptyRenderable
from ui.container import VAlign, VStackContainer
from ui.text import TextRenderable, InputRenderable, RichTextChunk, RichText
from ui.image import ImageRenderable

print_queue = []
frame = 0

def print_line(line: RichTextChunk | RichText | str) -> None:
    # TODO: Rich text
    print_queue.append(RichText.from_value(line))

def ui_process():
    if not print_queue: return

    global frame
    frame += 1

    if frame % 3 != 0: return
    
    line = print_queue.pop(0)
    TextRenderable(line, parent=text_container)

def clear_lines() -> None:
    text_container.clear_children()

ui_root = EmptyRenderable()
bg_img = ImageRenderable("static/bg/manor_fireplace.jpg", parent=ui_root)
big_container = VStackContainer(v_align=VAlign.BOTTOM, parent=ui_root)
input_box = InputRenderable(
    # "[cmd]",
    "[dialog -> Villager]",
    parent=big_container,
)
text_container = VStackContainer(v_align=VAlign.BOTTOM, parent=big_container)

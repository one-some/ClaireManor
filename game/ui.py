import pyray as rl
from ui.vector2 import Vector2
from ui.renderable import Renderable, EmptyRenderable
from ui.container import VAlign, VStackContainer
from ui.text import TextRenderable, InputRenderable, RichTextChunk, RichText

def print_line(line: str) -> None:
    # TODO: Rich text
    text_container.children.append(TextRenderable(
        # RichTextChunk(line, color=rl.Color(0x90, 0x90, 0x90, 0XFF))
        RichText.from_value(line)
    ))

def submit_command(command: str) -> None:
    print_line(command)

ui_root = EmptyRenderable()
big_container = VStackContainer(v_align=VAlign.BOTTOM, parent=ui_root)
input_box = InputRenderable(
    "Type to do something...",
    on_submit=submit_command,
    parent=big_container,
)
text_container = VStackContainer(v_align=VAlign.BOTTOM, parent=big_container)

text_container.children.append(TextRenderable(
    RichText([
        RichTextChunk("[evil] "),
        RichTextChunk("Hello! Superman speaking!", color=rl.RED),
    ])
))

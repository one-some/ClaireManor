from __future__ import annotations

import pyray as rl

import font
from ui.vector2 import Vector2
from ui.renderable import Renderable, EmptyRenderable
from ui.container import VAlign, VStackContainer


# TODO:
class RichText:
    pass

class RichTextChunk:
    def __init__(
        self,
        text: str,
        color: rl.Color = rl.WHITE
    ) -> None:
        self.text = text
        self.color = color

class TextRenderable(Renderable):
    def __init__(self, text: str | RichText, **kwargs):
        super().__init__(**kwargs)
        self.text = text

    def render_self(self) -> None:
        rl.draw_text_ex(
            draw_font,
            self.text,
            self.position.to_raylib(),
            draw_font.baseSize,
            0,
            rl.WHITE
        )

    def measure(self) -> Vector2:
        return Vector2.from_raylib(rl.measure_text_ex(
            draw_font,
            self.text,
            draw_font.baseSize,
            0,
        ))

class InputRenderable(Renderable):
    def __init__(
            self,
            placeholder: str = "",
            on_submit: Optional[Callable] = None,
            **kwargs
        ):
        super().__init__(**kwargs)
        self.placeholder = placeholder
        self.on_submit = on_submit
        self.buffer = ""

    def measure(self) -> Vector2:
        return Vector2.from_raylib(rl.measure_text_ex(
            draw_font,
            self.buffer or self.placeholder,
            draw_font.baseSize,
            0,
        ))

    def render_self(self) -> None:
        # Let's maybe not do tooo much logic in render. but whatever

        while char := rl.get_char_pressed():
            self.buffer += chr(char)

        if (
            self.buffer and
            # get_char_pressed automatically does echoing
            (
                rl.is_key_pressed(rl.KEY_BACKSPACE) or
                rl.is_key_pressed_repeat(rl.KEY_BACKSPACE)
            )
        ):
            self.buffer = self.buffer[:-1]


        if rl.is_key_pressed(rl.KEY_ENTER):
            if self.on_submit:
                self.on_submit(self.buffer)
            self.buffer = ""

        chunk = RichTextChunk(self.buffer)

        if not self.buffer:
            chunk = RichTextChunk(
                self.placeholder,
                color=rl.GRAY
            )

        rl.draw_text_ex(
            draw_font,
            chunk.text,
            self.position.to_raylib(),
            draw_font.baseSize,
            0,
            chunk.color
        )

root = EmptyRenderable()
container = VStackContainer(v_align=VAlign.BOTTOM)
root.children.append(container)
container.children.append(TextRenderable(
    "Welcome to The Manor Claire.\nSay 'help' or '?' at any time for a guide on how to play the game."
))
container.children.append(TextRenderable("Normal"))
container.children.append(TextRenderable("XXXXX"))
container.children.append(TextRenderable("EVIL"))
container.children.append(InputRenderable(
    "Type to do something...",
    on_submit=lambda x: print(x)
))

rl.set_trace_log_level(rl.TraceLogLevel.LOG_WARNING)
rl.init_window(800, 450, "The Manor Claire")
rl.set_window_state(rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)

# See font.py for my rant on fonts
draw_font = font.load_jagged_ttf("static/unscii-16.ttf", 16);

while not rl.window_should_close():
    root.reflow_layout(Vector2(
        rl.get_render_width(),
        rl.get_render_height()
    ))

    rl.begin_drawing()
    rl.clear_background(rl.BLACK)

    root.render()

    rl.end_drawing()
rl.close_window()

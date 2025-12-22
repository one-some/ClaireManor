from __future__ import annotations

import pyray as rl
from ui.vector2 import Vector2
from ui.renderable import Renderable
from typing import Optional, Callable

class RichTextChunk:
    def __init__(
        self,
        text: str,
        color: rl.Color = rl.WHITE
    ) -> None:
        self.text = text
        self.color = color

class RichText:
    def __init__(self, nodes: list[RichTextChunk]) -> None:
        assert isinstance(nodes, list)
        self.nodes = nodes

    @classmethod
    def from_value(cls, value: str| RichTextChunk | list[RichTextChunk]) -> RichText:
        if isinstance(value, cls):
            return value
        elif isinstance(value, list):
            return cls(value)
        elif isinstance(value, str):
            return cls.from_str(value)
        elif isinstance(value, RichTextChunk):
            return cls([value])
        assert False

    @classmethod
    def from_str(cls, string: str) -> list[RichTextChunk]:
        return cls([RichTextChunk(string)])

    def get_raw(self) -> str:
        return "".join([n.text for n in self.nodes])

class TextRenderable(Renderable):
    def __init__(self, text: str | RichText, **kwargs):
        super().__init__(**kwargs)
        self.text = RichText.from_value(text)

    def render_self(self) -> None:
        pointer = self.position.copy()

        for chunk in self.text.nodes:
            lines = chunk.text.split("\n")

            while lines:
                line = lines.pop()
                box = Vector2.from_raylib(rl.measure_text_ex(
                    self.font,
                    line,
                    self.font.baseSize,
                    0,
                ))

                rl.draw_text_ex(
                    self.font,
                    line,
                    pointer.to_raylib(),
                    self.font.baseSize,
                    0,
                    chunk.color
                )

                pointer.x += box.x

                # Always add n-1 lines y-wise
                if lines:
                    pointer.x = 0
                    pointer.y += self.font.baseSize

    def measure(self) -> Vector2:
        return Vector2.from_raylib(rl.measure_text_ex(
            self.font,
            self.text.get_raw(),
            self.font.baseSize,
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

        self.history = []
        self.history_idx = 0

    def measure(self) -> Vector2:
        return Vector2.from_raylib(rl.measure_text_ex(
            self.font,
            self.buffer or self.placeholder,
            self.font.baseSize,
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


        # Submit
        if rl.is_key_pressed(rl.KEY_ENTER):
            if not self.buffer:
                # Type something!
                return

            self.history.append(self.buffer)

            if self.on_submit:
                self.on_submit(self.buffer)

            self.buffer = ""
            self.history_idx = 0


        # History
        touched_history = True
        if rl.is_key_pressed(rl.KEY_UP):
            self.history_idx -= 1
        elif rl.is_key_pressed(rl.KEY_DOWN):
            self.history_idx += 1
        else:
            touched_history = False

        if touched_history:
            self.history_idx = min(0, self.history_idx)
            self.history_idx = max(self.history_idx, -len(self.history))

            if self.history_idx == 0:
                self.buffer = ""
            else:
                self.buffer = self.history[self.history_idx]

        chunk = RichTextChunk(self.buffer)

        if not self.buffer:
            chunk = RichTextChunk(
                self.placeholder,
                color=rl.GRAY
            )

        rl.draw_text_ex(
            self.font,
            chunk.text,
            self.position.to_raylib(),
            self.font.baseSize,
            0,
            chunk.color
        )

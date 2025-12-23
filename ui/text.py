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

    @staticmethod
    def tag_to_style(tag: str) -> rl.Color:
        # NOTE: "style" is currently just color. In the future I want to support
        # many types of text styling: sizes, brightness, animations, bg color,
        # gradients, masks, etc...

        match tag:
            case "act":
                return rl.ORANGE

        raise RuntimeError(f"Unexpected tag '{tag}'")

    @classmethod
    def from_str(cls, string: str) -> list[RichTextChunk]:
        default = {"type": "text", "content": ""}
        bits = [dict(default)]

        for char in string:
            if char == "<":
                new = dict(default)
                new["type"] = "tag"
                bits.append(new)
                continue
            elif char == ">":
                assert bits[-1]["type"] == "tag"
                bits.append(dict(default))
                continue
            bits[-1]["content"] += char

        # Could be one pass if I hated myself
        out = []
        style_stack = []

        for bit in bits:
            if bit["type"] == "text":
                # I wish there was a .get for lists
                color = style_stack[-1]["color"] if style_stack else rl.WHITE
                out.append(RichTextChunk(bit["content"], color=color))
                continue

            # Tag
            assert bit["type"] == "tag"
            assert bit["content"]

            closing = bit["content"][0] == "/"
            tag_name = bit["content"].lstrip("/")

            if closing:
                assert style_stack
                assert style_stack[-1]["tag"] == tag_name
                style_stack.pop()
                continue

            style_stack.append({
                "tag": tag_name,
                "color": cls.tag_to_style(tag_name)
            })

        return out

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

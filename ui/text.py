from __future__ import annotations

import pyray as rl
from ui.vector2 import Vector2
from ui.renderable import Renderable
from typing import Optional, Callable
from game import state

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

        return {
            "act": rl.ORANGE,
            "noun": rl.WHITE,
            "red": rl.RED,
            "gray": rl.GRAY,
            "darkgreen": rl.DARKGREEN,
            "gold": rl.GOLD,
            "blue": rl.BLUE,
        }[tag]

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
                color = style_stack[-1]["color"] if style_stack else rl.LIGHTGRAY
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
        self.inserted_break_indices = []

    def reflow_layout_self(self, allocated_size: Vector2) -> None:
        # Calculate text wrapping. Probably expensive w/ these ffi calls!!!
        self.inserted_break_indices.clear()
        last_space_index = -1
        line_width = 0.0

        for i, char in enumerate(self.text.get_raw()):
            glyph_index = rl.get_glyph_index(self.font, ord(char))
            line_width += self.font.glyphs[glyph_index].advanceX

            if char == " ":
                last_space_index = i
            elif char == "\n":
                line_width = 0.0
                last_space_index = -1

            if line_width > allocated_size.x:
                if last_space_index == -1:
                    # break on letter if needed
                    self.inserted_break_indices.append(i)
                else:
                    self.inserted_break_indices.append(last_space_index)
                last_space_index = -1
                line_width = 0.0

    def get_wrapped_chunk_text(self) -> dict:
        # TODO: Cache per frame/inserted_break_indices
        out = {}
        big_i = 0

        for chunk in self.text.nodes:
            text = ""
            for char in chunk.text:
                text += char
                if big_i in self.inserted_break_indices:
                    text += "\n"
                big_i += 1
            out[chunk] = text

        return out

    def render_self(self) -> None:
        pointer = self.position.copy()

        for chunk, text in self.get_wrapped_chunk_text().items():
            lines = text.split("\n")

            while lines:
                line = lines.pop(0)
                box = Vector2.from_raylib(rl.measure_text_ex(
                    self.font,
                    line,
                    self.font_size,
                    0,
                ))

                rl.draw_text_ex(
                    self.font,
                    line,
                    pointer.to_raylib(),
                    self.font_size,
                    0,
                    chunk.color
                )

                pointer.x += box.x

                # Always add n-1 lines y-wise
                if lines:
                    pointer.x = 0
                    pointer.y += self.font_size

    def measure(self) -> Vector2:
        return Vector2.from_raylib(rl.measure_text_ex(
            self.font,
            "".join(self.get_wrapped_chunk_text().values()),
            self.font_size,
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

    def get_used_text(self) -> str:
        if self.buffer:
            return self.buffer

        if state.input_prompt:
            return state.input_prompt

        return self.placeholder

    def measure(self) -> Vector2:
        return Vector2.from_raylib(rl.measure_text_ex(
            self.font,
            self.get_used_text(),
            self.font_size,
            0,
        ))

    def process(self) -> None:
        if state.enter_future:
            if rl.is_key_pressed(rl.KEY_ENTER):
                state.enter_future.set_result(None)
            return

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

            if state.input_future:
                state.input_future.set_result(self.buffer)
            else:
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


    def render_self(self) -> None:
        # Let's maybe not do tooo much logic in render. but whatever
        self.process()

        chunk = RichTextChunk(self.get_used_text())

        if not self.buffer:
            chunk.color = rl.GRAY

        rl.draw_text_ex(
            self.font,
            chunk.text,
            self.position.to_raylib(),
            self.font_size,
            0,
            chunk.color
        )

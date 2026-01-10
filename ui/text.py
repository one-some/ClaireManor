from __future__ import annotations

import asyncio
import pyray as rl
from typing import Optional, Callable

from ui.vector2 import Vector2
from ui.renderable import Renderable

TEXT_COLOR = rl.Color(0xB0, 0xB0, 0xB0, 0xFF)

class RichTextChunk:
    def __init__(
        self,
        text: str,
        color: rl.Color = TEXT_COLOR
    ) -> None:
        self.text = text
        self.color = color

class RichText:
    def __init__(self, nodes: list[RichTextChunk]) -> None:
        # TODO: Umm... just put from_value here..??!?!?
        assert isinstance(nodes, list), "Pls remember to use from_value"
        self.nodes = nodes

    def get_n_leading(self, n: int) -> RichText:
        # Gets leading n characters while preserving rich attributes.
        # NOTE: May be called a lot for typewriter effect. Be nimble, be quick!
        # Jump over a candlestick!

        nodes = []
        for node in self.nodes:
            partial_node = RichTextChunk("", color=node.color)
            nodes.append(partial_node)

            for char in node.text:
                if not n: break
                partial_node.text += char
                n -= 1

            if not n:
                break

        return RichText(nodes)

    def get_raw(self) -> str:
        return "".join([n.text for n in self.nodes])

    def __len__(self) -> int:
        return sum([len(n.text) for n in self.nodes])

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
        assert False, f"Won't cast from {type(value)}"

    @staticmethod
    def tag_to_style(tag: str) -> rl.Color:
        # NOTE: "style" is currently just color. In the future I want to support
        # many types of text styling: sizes, brightness, animations, bg color,
        # gradients, masks, etc...

        return {
            "act": rl.ORANGE,
            "noun": rl.WHITE,
            "red": rl.RED,
            "white": rl.WHITE,
            "gray": rl.DARKGRAY,
            "green": rl.GREEN,
            "gold": rl.GOLD,
            "yellow": rl.YELLOW,
            "blue": rl.BLUE,
            "claire": rl.DARKPURPLE,
            "darkgreen": rl.DARKGREEN,
            "darkred": rl.Color(0x99, 0x11, 0x11, 0xFF),
            "darkblue": rl.DARKBLUE,
            "palegreen": rl.Color(0x77, 0xA6, 0x84, 0xFF),
            "paleblue": rl.Color(0x77, 0x80, 0xA6, 0xFF),
            "paleyellow": rl.Color(0x9E, 0xAB, 0x60, 0xFF),
        }[tag]

    @classmethod
    def from_str(cls, string: str) -> RichText:
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
                color = style_stack[-1]["color"] if style_stack else TEXT_COLOR
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

        return RichText(out)

class TextRenderable(Renderable):
    def __init__(self, text: str | RichText, **kwargs):
        super().__init__(**kwargs)
        self.text = RichText.from_value(text)
        assert isinstance(self.text, RichText)
        self.inserted_break_indices = []

    def reflow_layout_self(self, allocated_size: Vector2) -> None:
        # Calculate text wrapping. Probably expensive w/ these ffi calls!!!
        self.inserted_break_indices.clear()
        last_space_index = -1
        line_width = 0.0
        current_word_width = 0.0
        scale_factor = self.font_size / self.font.baseSize

        # Spudge it to make it seem more friendly
        max_line_width = allocated_size.x - 24.0

        for i, char in enumerate(self.text.get_raw()):
            glyph_index = rl.get_glyph_index(self.font, ord(char))
            char_width = self.font.glyphs[glyph_index].advanceX * scale_factor

            if char == "\n":
                line_width = 0.0
                current_word_width = 0.0
                last_space_index = -1
                continue

            line_width += char_width
            current_word_width += char_width

            if char == " ":
                last_space_index = i
                current_word_width = 0.0

            if line_width > max_line_width:
                if last_space_index != -1:
                    self.inserted_break_indices.append(last_space_index)
                    line_width = current_word_width
                else:
                    # break on letter if needed
                    self.inserted_break_indices.append(i)
                    line_width = 0.0
                    current_word_width = 0.0
                last_space_index = -1

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

    def render_self(self, position: Vector2) -> None:
        pointer = position.copy()

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
                    pointer.x = position.x
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
            **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.placeholder = placeholder
        self.prompt_str = None
        self.future = None
        self.input_disabled = False

        self.buffer = ""

        self.history = []
        self.history_idx = 0

    async def prompt(self, prompt: str) -> str:
        self.prompt_str = prompt

        assert not self.future
        loop = asyncio.get_running_loop()
        self.future = loop.create_future()

        return await self.future

    async def wait_for_enter(self) -> None:
        self.input_disabled = True
        self.prompt_str = "[press enter to continue]"

        assert not self.future
        loop = asyncio.get_running_loop()
        self.future = loop.create_future()

        await self.future
        self.input_disabled = False

        return 

    def get_visual_text(self) -> str:
        if self.buffer:
            return self.buffer + "█"

        if self.prompt_str:
            return self.prompt_str

        return self.placeholder

    def measure(self) -> Vector2:
        return Vector2.from_raylib(rl.measure_text_ex(
            self.font,
            self.get_visual_text(),
            self.font_size,
            0,
        ))

    def process(self) -> None:
        # Submit
        if rl.is_key_pressed(rl.KEY_ENTER):
            if self.future:
                self.future.set_result(self.buffer)
                self.future = None
                self.prompt_str = None

            self.history.append(self.buffer)

            self.buffer = ""
            self.history_idx = 0

        if self.input_disabled:
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


    def render_self(self, position: Vector2) -> None:
        # Let's maybe not do tooo much logic in render. but whatever
        self.process()

        chunk = RichTextChunk(self.get_visual_text())

        if not self.buffer:
            chunk.color = rl.GRAY

        rl.draw_text_ex(
            self.font,
            chunk.text,
            position.to_raylib(),
            self.font_size,
            0,
            chunk.color
        )

from __future__ import annotations

import pyray as rl

import font

rl.init_window(800, 450, "The Manor Claire")
rl.set_window_state(rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)

# See font.py for my rant on fonts
draw_font = font.load_jagged_ttf("font/unscii-16.ttf", 16);

class Vector2:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    @classmethod
    def zero(cls) -> Vector2:
        return cls(0, 0)

    def to_raylib(self) -> rl.Vector2:
        return rl.Vector2(self.x, self.y)

class Renderable:
    # I'm trying out this kwargs pattern for passing arguments up the
    # inheritence chain. I was worried it wouldn't catch parameter typos until
    # it dawned upon me that I don't use autocomplete

    def __init__(self, **kwargs) -> None:
        self.position = kwargs.pop("position", Vector2.zero())
        self.children: list[Renderable] = []

        # All the arguments should have been eaten before here. Otherwise, the
        # argument is misspelled. We're all picky eaters here
        assert not kwargs

    def render_self(self) -> None:
        raise NotImplementedError

    def render(self) -> None:
        # Always render children behind parent
        for child in self.children:
            child.render()

        self.render_self()

class EmptyRenderable(Renderable):
    def render_self(self) -> None:
        # Won't raise NotImplementedError
        pass

# TODO:
class RichText:
    pass

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

root = EmptyRenderable()
root.children.append(TextRenderable("hello bro"))
root.children.append(TextRenderable("EVIL", position=Vector2(40, 40)))

while not rl.window_should_close():
    rl.begin_drawing()
    rl.clear_background(rl.BLACK)

    root.render()

    rl.end_drawing()
rl.close_window()

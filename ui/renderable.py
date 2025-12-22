from __future__ import annotations

import pyray as rl
from ui.vector2 import Vector2

class Renderable:
    # I'm trying out this kwargs pattern for passing arguments up the
    # inheritence chain. I was worried it wouldn't catch parameter typos until
    # it dawned upon me that I don't use autocomplete

    font: rl.Font

    def __init__(self, **kwargs) -> None:
        self.position = kwargs.pop("position", Vector2.zero())
        self.static_size = kwargs.pop("static_size", None)

        if "parent" in kwargs:
            kwargs.pop("parent").add_child(self)

        self.children: list[Renderable] = []

        # All the arguments should have been eaten before here. Otherwise, the
        # argument is misspelled. We're all picky eaters here
        assert not kwargs

    def add_child(self, child: Renderable) -> None:
        self.children.append(child)

    def render_self(self) -> None:
        raise NotImplementedError

    def render(self) -> None:
        # Always render children behind parent
        for child in self.children:
            child.render()

        self.render_self()

    def reflow_layout(self, allocated_size: Vector2) -> None:
        for child in self.children:
            child.reflow_layout(allocated_size)

    def measure(self) -> Vector2:
        # Content size

        # TODO: Per-frame cache? This tends to compute
        return Vector2.zero()

class EmptyRenderable(Renderable):
    # Designed for logical grouping

    def render_self(self) -> None:
        # Won't raise NotImplementedError
        pass

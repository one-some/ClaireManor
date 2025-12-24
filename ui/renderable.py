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

        # An "inactive" node isn't processed or rendered
        self.active = kwargs.pop("active", True)

        # Just for debug
        self.name = kwargs.pop("name", None)

        self._children: list[Renderable] = []

        # All the arguments should have been eaten before here. Otherwise, the
        # argument is misspelled. We're all picky eaters here
        assert not kwargs

    @property
    def active_children(self) -> list[Renderable]:
        return [x for x in self._children if x.active]
    
    def add_child(self, child: Renderable) -> None:
        self._children.append(child)
        
    def clear_children(self) -> None:
        self._children.clear()

    def render_self(self) -> None:
        raise NotImplementedError

    def render(self) -> None:
        # Always render children behind parent
        for child in self.active_children:
            child.render()

        self.render_self()

    def reflow_layout(self, allocated_size: Vector2) -> None:
        self.reflow_layout_self(allocated_size)
        for child in self.active_children:
            child.reflow_layout(allocated_size)

    def reflow_layout_self(self, allocated_size: Vector2) -> None:
        pass

    def measure(self) -> Vector2:
        # Content size

        # TODO: Per-frame cache? This tends to compute
        return Vector2.zero()

    def __repr__(self):
        if self.name:
            return f"<{self.__class__.__name__}: {self.name}>"
        return f"<{self.__class__.__name__}>"

class EmptyRenderable(Renderable):
    # Designed for logical grouping

    def render_self(self) -> None:
        # Won't raise NotImplementedError
        pass

from enum import Enum
from ui.vector2 import Vector2
from ui.renderable import Renderable

class VAlign(Enum):
    TOP = 0
    CENTER = 1
    BOTTOM = 2

class Container(Renderable):
    def __init__(self, **kwargs) -> None:
        self.v_align = kwargs.pop("v_align", VAlign.TOP)
        self.gap = kwargs.pop("gap", 2)
        self._cached_reflow_size = Vector2.zero()
        super().__init__(**kwargs)

    def render(self):
        for child in self.children:
            child.render()

    def render_self(self) -> None:
        pass

    def reflow_layout(self, allocated_size: Vector2) -> None:
        raise NotImplementedError

    def measure(self) -> Vector2:
        # For now, containers are guaranteed their target size
        return self.static_size or Vector2(0, 0)

class VStackContainer(Container):
    def reflow_layout(self, allocated_size: Vector2) -> None:
        self._cached_reflow_size = allocated_size

        wiggle_room = allocated_size.y - (self.gap * (len(self.children) - 1))
        dynamic_children = len(self.children)

        for child in self.children:
            if not child.static_size:
                continue

            wiggle_room -= child.static_size.y
            child.reflow_layout(Vector2(allocated_size.x, child.static_size.y))
            dynamic_children -= 1

        for child in self.children:
            if child.static_size:
                continue
            child.reflow_layout(Vector2(
                allocated_size.x,
                wiggle_room / dynamic_children
            ))

        assert self.v_align != VAlign.CENTER

        pos_y = 0
        iterator = self.children

        if self.v_align == VAlign.BOTTOM:
            pos_y = allocated_size.y
            iterator = reversed(iterator)

        for child in iterator:
            child_size = child.measure()

            child.position.x = 0

            if self.v_align == VAlign.BOTTOM:
                pos_y -= child_size.y + self.gap
                child.position.y = pos_y
            else:
                child.position.y = pos_y
                pos_y += child_size.y + self.gap

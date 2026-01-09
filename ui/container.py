from enum import Enum
from ui.vector2 import Vector2
from ui.renderable import Renderable

class VAlign(Enum):
    TOP = 0
    CENTER = 1
    BOTTOM = 2

class HAlign(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2

class Container(Renderable):
    def __init__(self, **kwargs) -> None:
        self.v_align = kwargs.pop("v_align", VAlign.TOP)
        self.h_align = kwargs.pop("h_align", HAlign.LEFT)
        self.padding = kwargs.pop("padding", Vector2.zero())
        self.gap = kwargs.pop("gap", 2)
        self._cached_reflow_size = Vector2.zero()
        super().__init__(**kwargs)

    def render(self, position) -> None:
        super().render(position + self.padding / 2)

    def render_self(self, position: Vector2) -> None:
        pass

    def reflow_layout(self, allocated_size: Vector2) -> None:
        raise NotImplementedError

    def measure(self) -> Vector2:
        # For now, containers are guaranteed their target size
        return (self.static_size or self._cached_reflow_size) + self.padding

class VStackContainer(Container):
    def reflow_layout(self, allocated_size: Vector2) -> None:
        self._cached_reflow_size = allocated_size

        content_size = allocated_size - self.padding
        wiggle_room = content_size.y - (self.gap * (len(self.active_children) - 1))
        dynamic_children = len(self.active_children)

        for child in self.active_children:
            if not child.static_size:
                continue

            wiggle_room -= child.static_size.y
            child.reflow_layout(Vector2(content_size.x, child.static_size.y))
            dynamic_children -= 1

        for child in self.active_children:
            if child.static_size:
                continue
            child.reflow_layout(Vector2(
                content_size.x,
                wiggle_room / dynamic_children
            ))

        max_width = 0
        for child in self.active_children:
            child_size = child.measure()
            if child_size.x > max_width:
                max_width = child_size.x
        self._cached_reflow_size = Vector2(max_width, allocated_size.y)

        assert self.v_align != VAlign.CENTER

        pos_y = 0
        iterator = self.active_children

        if self.v_align == VAlign.BOTTOM:
            pos_y = content_size.y
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

class HStackContainer(Container):
    def reflow_layout(self, allocated_size: Vector2) -> None:
        self._cached_reflow_size = allocated_size

        content_size = allocated_size - self.padding
        wiggle_room = content_size.x - (self.gap * (len(self.active_children) - 1))
        dynamic_children = len(self.active_children)

        for child in self.active_children:
            if not child.static_size:
                continue

            wiggle_room -= child.static_size.x
            child.reflow_layout(Vector2(content_size.x, child.static_size.y))
            dynamic_children -= 1

        for child in self.active_children:
            if child.static_size:
                continue
            child.reflow_layout(Vector2(
                wiggle_room / dynamic_children,
                content_size.y,
            ))

        max_height = 0
        for child in self.active_children:
            child_size = child.measure()
            if child_size.y > max_height:
                max_height = child_size.y
        self._cached_reflow_size = Vector2(allocated_size.x, max_height)

        assert self.h_align != HAlign.CENTER

        pos_x = 0
        iterator = self.active_children

        if self.h_align == HAlign.RIGHT:
            pos_x = content_size.x
            iterator = reversed(iterator)

        for child in iterator:
            child_size = child.measure()

            child.position.y = 0

            if self.h_align == HAlign.RIGHT:
                pos_x -= child_size.x + self.gap
                child.position.x = pos_x
            else:
                child.position.x = pos_x
                pos_x += child_size.x + self.gap

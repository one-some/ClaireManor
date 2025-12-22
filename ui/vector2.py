from __future__ import annotations
import pyray as rl

class Vector2:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    @classmethod
    def zero(cls) -> Vector2:
        return cls(0, 0)

    @classmethod
    def from_raylib(cls, v: rl.Vector2) -> Vector2:
        return cls(v.x, v.y)

    def to_raylib(self) -> rl.Vector2:
        return rl.Vector2(self.x, self.y)

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

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

    def copy(self) -> Vector2:
        return Vector2(self.x, self.y)

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"


    def _math_op(self, other: Any, op: callable) -> Any:
        # I don't know how many vector ops we do but this could come and bit us
        # later performance-wise BUT i love being lazy

        if isinstance(other, Vector2):
            return Vector2(op(self.x, other.x), op(self.y, other.y))

        assert isinstance(other, (int, float))
        # Member-wise
        return Vector2(op(self.x, other), op(self.y, other))

    def __add__(self, other: Any) -> Any: return self._math_op(other, lambda a, b: a + b)
    def __sub__(self, other: Any) -> Any: return self._math_op(other, lambda a, b: a - b)
    def __mul__(self, other: Any) -> Any: return self._math_op(other, lambda a, b: a * b)
    def __truediv__(self, other: Any) -> Any: return self._math_op(other, lambda a, b: a / b)

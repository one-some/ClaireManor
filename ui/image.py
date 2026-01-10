import pyray as rl
from typing import Optional

from ui.vector2 import Vector2
from ui.renderable import Renderable

class ImageRenderable(Renderable):
    def __init__(
            self,
            path: Optional[str] = None,
            is_bg_image: bool = False,
            scale: float = 1.0,
            **kwargs
        ):
        self.scale = scale
        super().__init__(**kwargs)

        self.loaded = False
        self.is_bg_image = is_bg_image

        if path:
            self.load(path)

    def load(self, path: str) -> None:
        assert path

        if self.loaded:
            self.loaded = False
            rl.unload_texture(self.texture)

        image = rl.load_image(path)

        if self.is_bg_image:
            factor = rl.get_render_width() // image.width
            rl.image_resize(image, image.width * factor, image.height * factor)
            rl.image_blur_gaussian(image, 4)

        self.texture = rl.load_texture_from_image(image)
        rl.unload_image(image)

        self.loaded = True

    def measure(self) -> Vector2:
        if self.is_bg_image:
            return Vector2.zero()
        return Vector2(self.texture.width * self.scale, self.texture.height * self.scale)

    def reflow_layout_self(self, allocated_size: Vector2) -> None:
        if not self.loaded:
            return

        if self.is_bg_image:
            self.scale = max(
                allocated_size.x / self.texture.width,
                allocated_size.y / self.texture.height,
            )

            scaled = Vector2(
                self.texture.width,
                self.texture.height
            ) * self.scale

            self.position = (allocated_size - scaled) / 2

    def render_self(self, position) -> None:
        if not self.loaded:
            return

        alpha = 0x66
        tint = rl.Color(alpha, alpha, alpha, 0xFF) if self.is_bg_image else rl.WHITE

        rl.draw_texture_ex(
            self.texture,
            position.to_raylib(),
            0.0,
            self.scale,
            tint,
        )


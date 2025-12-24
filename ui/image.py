import pyray as rl
from ui.vector2 import Vector2
from ui.renderable import Renderable

# NOTE: Hardcoded for bg image...
class ImageRenderable(Renderable):
    def __init__(self, path: str, **kwargs):
        super().__init__(**kwargs)

        image = rl.load_image(path)
        factor = rl.get_render_width() // image.width

        rl.image_resize(image, image.width * factor, image.height * factor)
        rl.image_blur_gaussian(image, 10)

        self.texture = rl.load_texture_from_image(image)
        rl.unload_image(image)

        self.scale = 1.0

    def reflow_layout_self(self, allocated_size: Vector2) -> None:
        self.scale = max(
            allocated_size.x / self.texture.width,
            allocated_size.y / self.texture.height,
        )

    def render_self(self) -> None:
        rl.draw_texture_ex(
            self.texture,
            self.position.to_raylib(),
            0.0,
            self.scale,
            rl.Color(0x44, 0x44, 0x44, 0xFF)
        )


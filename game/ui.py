import time
import asyncio
import pyray as rl
from pathlib import Path
from typing import Optional

from ui.vector2 import Vector2
from ui.renderable import Renderable, EmptyRenderable, OverlayRenderable
from ui.container import VAlign, VStackContainer, HStackContainer, Container
from ui.text import TextRenderable, InputRenderable, RichTextChunk, RichText
from ui.image import ImageRenderable

class Fade:
    active_fade = None

    def __init__(
        self,
        target: float,
        speed: float = 0.005,
    ) -> None:
        self.target = target
        self.speed = speed

        assert self.target >= 0.0
        assert self.target <= 1.0

        loop = asyncio.get_running_loop()
        self.future = loop.create_future()

    async def wait_for(self) -> None:
        Fade.active_fade = self
        await self.future

    def step(self) -> None:
        alpha = overlay_rect.color[3] / 0xFF

        delta = self.target - alpha
        # HACK: Avoid div by zero if we're right on the money
        delta = delta or 0.0001

        sign = delta / abs(delta)
        inch = sign * self.speed

        alpha = max(0.0, min(1.0, alpha + inch))
        Fade.set_overlay_alpha(alpha)

        if (
            (sign == -1 and alpha <= self.target)
            or
            (sign == 1 and alpha >= self.target)
        ):
            self.future.set_result(None)
            Fade.active_fade = None

    @classmethod
    def step_active(cls) -> None:
        if not cls.active_fade:
            return
        cls.active_fade.step()

    @staticmethod
    def set_overlay_alpha(alpha: float) -> None:
        overlay_rect.color = (0x0, 0x0, 0x0, int(0xFF * alpha))


def ui_process() -> None:
    Fade.step_active()

def switch_active_text_container(cont: Renderable) -> None:
    global active_text_container

    active_text_container.active = False
    active_text_container = cont
    active_text_container.active = True

def change_background(background: str) -> None:
    bg_path = Path("static/bg") / f"{background}.jpg"

    if not bg_path.is_file():
        bg_img.loaded = False
        return

    bg_img.load(str(bg_path))

ui_root = EmptyRenderable()
bg_img = ImageRenderable(is_bg_image=True, parent=ui_root)

big_container = VStackContainer(
    parent=ui_root,
    name="BIG",
)

overlay_rect = OverlayRenderable(rl.BLANK, parent=ui_root)

battle_stats = TextRenderable(
    RichText.from_value(
        "<gray>▓     🯆 </gray>YOU - [LEVEL 26]\n" \
        "<gray>▓   HP: </gray><red>100 [█████████▌]</red>\n" \
        "<gray>▓ STAM: </gray><darkgreen>100</darkgreen>"
    ),
    parent=big_container,
    active=False
)

story_text_container = VStackContainer(
    v_align=VAlign.BOTTOM,
    parent=big_container,
    name="StoryText"
)

battle_text_container = VStackContainer(
    v_align=VAlign.BOTTOM,
    parent=big_container,
    active=False,
    name="BattleText"
)

input_box = InputRenderable(
    "[...]",
    # "[dialog -> Villager]",
    parent=big_container,
)

active_text_container = story_text_container

print(big_container.active_children)

# HSPLIT THE TWO PARTIES HEALTHWISE

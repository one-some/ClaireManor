import time
import asyncio
import pyray as rl

from ui.vector2 import Vector2
from ui.renderable import Renderable, EmptyRenderable, OverlayRenderable
from ui.container import VAlign, VStackContainer, HStackContainer, Container
from ui.text import TextRenderable, InputRenderable, RichTextChunk, RichText
from ui.image import ImageRenderable
from game import state

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

        # Muahahaha
        await asyncio.sleep(1.0)

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

async def rich_drip_feed(
    line: RichTextChunk | RichText | str,
    chars_per_second: int = 35
) -> None:
    # TODO: Implement a way to slow text on punctuation. Gonna need another
    # approach. Naive approach is too slow, and this one doesn't operate on a
    # per-char basis.

    rt = RichText.from_value(line)
    total_len = len(rt)
    current_len = 0

    # OMG, this is so much better than always doing int(time.time()). I feel dumb
    start_time = time.monotonic()

    while current_len < total_len:
        if rl.is_key_pressed(rl.KEY_ENTER):
            # TODO: Go faster or skip?? Which is better!?!?!?!?!?!?!?! XP
            yield rt
            return

        elapsed_sec = time.monotonic() - start_time
        target_len = int(elapsed_sec * chars_per_second)
        target_len = min(target_len, total_len)

        if target_len > current_len:
            current_len = target_len
            yield rt.get_n_leading(current_len)

        if current_len < total_len:
            await asyncio.sleep(0.0)

async def print_dialog(line: RichTextChunk | RichText | str) -> None:
    text_renderable = TextRenderable("", parent=active_text_container)

    async for rich in rich_drip_feed(line):
        text_renderable.text = rich

    await enter_to_continue()

async def add_dialog(name: str, text: str) -> None:
    container = HStackContainer(padding=Vector2(20, 20), gap=10, parent=active_text_container)

    # HACK
    image = ImageRenderable(f"static/portraits/{name.lower()}.png", scale=2.0, parent=container)

    text_renderable = TextRenderable("", parent=container)
    async for rich in rich_drip_feed(
        f'<gray>{name}: </gray>\n"{text}"',
        chars_per_second=15
    ):
        text_renderable.text = rich

    await enter_to_continue()

async def print_line(line: RichTextChunk | RichText | str) -> None:
    # I had to get myself to calm down with this one. This function is used like
    # everywhere so in my mind I was like "this is async creep on CRAZY MODE
    # STEROIDS" but it functions exactly how I like it with the small side
    # effect of things in this async game engine actually being async (shocker)

    text_renderable = TextRenderable(line, parent=active_text_container)

    # "Thinking" effect
    await asyncio.sleep(0.05)

def ui_process():
    Fade.step_active()

def clear_lines() -> None:
    active_text_container.clear_children()

async def enter_to_continue() -> None:
    state.input_prompt = "[ press enter to continue ]"

    loop = asyncio.get_running_loop()
    state.enter_future = loop.create_future()
    await state.enter_future

    state.input_prompt = None
    state.enter_future = None

async def prompt(placeholder: str) -> None:
    state.input_prompt = placeholder

    loop = asyncio.get_running_loop()
    state.input_future = loop.create_future()
    out = await state.input_future

    state.input_future = None
    state.input_prompt = None

    return out

async def ranged_prompt(start: int, end: int) -> None:
    range_string = f"{start}-{end}"
    target = None
    while True:
        number = await prompt(f"[choose a number {range_string}]")
        try:
            num = int(number)

            if num > end or num < start:
                await print_line(f"Please choose a number <red>{range_string}</red>! Try again.")
                continue

            return num
        except ValueError:
            await print_line(f"Please choose a <red>number</red> {range_string}! Try again.")

def switch_active_text_container(cont: Renderable):
    global active_text_container

    active_text_container.active = False
    active_text_container = cont
    active_text_container.active = True

ui_root = EmptyRenderable()
bg_img = ImageRenderable("static/bg/village_square.png", is_bg_image=True, parent=ui_root)

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
    "[cmd]",
    # "[dialog -> Villager]",
    parent=big_container,
)

active_text_container = story_text_container

print(big_container.active_children)

# HSPLIT THE TWO PARTIES HEALTHWISE

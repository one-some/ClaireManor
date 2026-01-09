import time
import asyncio
import pyray as rl

from game import ui
from game.io import wait_for_enter
from ui.vector2 import Vector2
from ui.text import TextRenderable, RichTextChunk, RichText
from ui.image import ImageRenderable
from ui.container import VAlign, VStackContainer, HStackContainer, Container

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

async def print_dialog(line: RichTextChunk | RichText | str, wait: bool = True) -> None:
    text_renderable = TextRenderable("", parent=ui.active_text_container)

    async for rich in rich_drip_feed(line):
        text_renderable.text = rich

    if wait:
        await wait_for_enter()

async def add_dialog(name: str, text: str) -> None:
    container = HStackContainer(padding=Vector2(20, 20), gap=10, parent=ui.active_text_container)

    # HACK
    image = ImageRenderable(f"static/portraits/{name.lower()}.png", scale=2.0, parent=container)

    text_renderable = TextRenderable("", parent=container)
    async for rich in rich_drip_feed(
        f'<gray>{name}: </gray>\n"{text}"',
        chars_per_second=15
    ):
        text_renderable.text = rich

    await wait_for_enter()

import asyncio
import pyray as rl

from ui.vector2 import Vector2
from ui.renderable import Renderable, EmptyRenderable
from ui.container import VAlign, VStackContainer, Container
from ui.text import TextRenderable, InputRenderable, RichTextChunk, RichText
from ui.image import ImageRenderable
from game import state

print_queue = []
frame = 0

class PrintQueueItem:
    def __init__(
        self,
        value: RichTextChunk | RichText | str,
        container: Container,
    ) -> None:
        self.value = value
        self.container = container

def print_line(line: RichTextChunk | RichText | str) -> None:
    # TODO: Rich text
    print_queue.append(PrintQueueItem(
        RichText.from_value(line),
        active_text_container
    ))

def ui_process():
    if not print_queue: return

    global frame
    frame += 1

    if frame % 3 != 0: return
    
    queue_item = print_queue.pop(0)
    TextRenderable(queue_item.value, parent=queue_item.container)

def clear_lines() -> None:
    active_text_container.clear_children()

async def enter_to_continue() -> None:
    loop = asyncio.get_running_loop()

    state.input_prompt = "[ press enter to continue ]"
    state.enter_future = loop.create_future()

    await state.enter_future

    state.input_prompt = None
    state.enter_future = None

async def prompt(placeholder: str) -> None:
    loop = asyncio.get_running_loop()

    state.input_prompt = placeholder
    state.input_future = loop.create_future()

    out = await state.input_future

    state.input_future = None
    state.input_prompt = None

    return out

def switch_active_text_container(cont: Renderable):
    global active_text_container

    active_text_container.active = False
    active_text_container = cont
    active_text_container.active = True

ui_root = EmptyRenderable()
bg_img = ImageRenderable("static/bg/village_square.png", parent=ui_root)

big_container = VStackContainer(
    parent=ui_root,
    name="BIG",
)

battle_stats = TextRenderable(
    RichText.from_value(
        "<gray>▓   🯆 </gray>YOU - [LEVEL 26]\n" \
        "<gray>▓ HP: </gray><red>100</red> " \
        "<gray>STAM: </gray><darkgreen>100</darkgreen>"
    ),
    parent=big_container,
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

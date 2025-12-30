import asyncio

from game import ui
from game import state
from ui.vector2 import Vector2
from ui.text import TextRenderable, RichTextChunk, RichText
from ui.container import VAlign, VStackContainer, HStackContainer, Container

async def print_line(line: RichTextChunk | RichText | str) -> None:
    # I had to get myself to calm down with this one. This function is used like
    # everywhere so in my mind I was like "this is async creep on CRAZY MODE
    # STEROIDS" but it functions exactly how I like it with the small side
    # effect of things in this async game engine actually being async (shocker)

    TextRenderable(line, parent=ui.active_text_container)

    # "Thinking" effect
    await asyncio.sleep(0.05)

def clear_lines() -> None:
    ui.active_text_container.clear_children()

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

async def choice_prompt(
    prompt: str,
    value: list | dict,
    include_back: bool = False
) -> None:
    await print_line(prompt)
    assert isinstance(value, (list, dict))

    # We need to be a dict so we can map Back on with seperate value (None)
    choices = value if isinstance(value, dict) else {v: v for v in value}

    if include_back:
        choices["<gray>Back</gray>"] = None

    for i, k in enumerate(choices.keys()):
        await print_line(f"{i + 1}. {k}")

    choice_idx = await ranged_prompt(1, len(choices)) - 1
    await print_line(" ")

    return list(choices.values())[choice_idx]


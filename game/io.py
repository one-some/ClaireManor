import asyncio

from game import ui
from ui.vector2 import Vector2
from ui.text import TextRenderable, RichTextChunk, RichText
from ui.container import VAlign, VStackContainer, HStackContainer, Container

# Convienence mappings
prompt = ui.input_box.prompt
wait_for_enter = ui.input_box.wait_for_enter

async def print_line(line: RichTextChunk | RichText | str, now: bool = False) -> None:
    # HACK: I made the last-minute decision to run print_dialog for most prints. It's ugly!
    if not now:
        from game.dialog import print_dialog
        await print_dialog(line, wait=False, chars_per_second=100)
        return

    TextRenderable(line, parent=ui.active_text_container)

    # "Thinking" effect
    await asyncio.sleep(0.05)

def clear_lines() -> None:
    ui.active_text_container.clear_children()

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


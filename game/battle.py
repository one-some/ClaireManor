from game import ui
from game.ui import print_line

def start_battle():
    ui.switch_active_text_container(ui.battle_text_container)

    print_line("It's time to battle!")

def end_battle():
    ui.switch_active_text_container(ui.story_text_container)

    print_line("Bai")

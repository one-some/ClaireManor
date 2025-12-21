
RUBRIC_COMPLIANCE = False

class Location:
    pass

phrases = [
    Command("look at", [Location]),
    Command(["find", "hunt for", "look for"], [Item]),
]

def find_matching_command(user_input: str) -> Optional[Command]:

    print(f"Sorry, I don't know verb ")
    return None

while True:
    user_input = input("Do what?> ")
    command = find_matching_command(user_input)

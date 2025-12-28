from __future__ import annotations

import random
from enum import Enum

class PronounSet(Enum):
    SHE = 0
    HE = 1
    THEY = 2
    IT = 3
    YOU = 4

    @classmethod
    def random(cls) -> PronounSet:
        return random.choice(list(cls))

    @classmethod
    def is_plural(cls, pronoun_set: PronounSet) -> bool:
        return pronoun_set in [cls.THEY, cls.YOU]

# A lot of Googling later...
PRONOUNS = {
    "subject": {
        PronounSet.SHE: "she",
        PronounSet.HE: "he",
        PronounSet.THEY: "they",
        PronounSet.IT: "it",
        PronounSet.YOU: "you",
    },

    "object": {
        PronounSet.SHE: "her",
        PronounSet.HE: "him",
        PronounSet.THEY: "them",
        # ? Not a linguist...
        PronounSet.IT: "it",
        PronounSet.YOU: "you",
    },

    "posessive_adjective": {
        PronounSet.SHE: "her",
        PronounSet.HE: "his",
        PronounSet.THEY: "their",
        PronounSet.IT: "its",
        PronounSet.YOU: "your",
    },

    "posessive_pronoun": {
        PronounSet.SHE: "hers",
        PronounSet.HE: "his",
        PronounSet.THEY: "theirs",
        PronounSet.IT: "its",
        PronounSet.YOU: "yours",
    },

    # Idk if this will ever be used lol
    "reflexive": {
        PronounSet.SHE: "herself",
        PronounSet.HE: "himself",
        PronounSet.THEY: "themself",
        PronounSet.IT: "itself",
        PronounSet.YOU: "yourself",
    }
}

PRONOUN_SET_MAPPING = {
    "he": PRONOUNS["subject"],
    "him": PRONOUNS["object"],
    "his": PRONOUNS["posessive_adjective"],
    "hers": PRONOUNS["posessive_pronoun"],
    "himself": PRONOUNS["reflexive"],
}

class LanguageProfile:
    def __init__(self, name: str, pronoun_set: PronounSet) -> None:
        self.name = name
        self.pronoun_set = pronoun_set

    def __repr__(self) -> str:
        return self.name

def format(string: str, **participants: dict[str, LanguageProfile]) -> str:
    assert all([isinstance(x, LanguageProfile) for x in participants.values()])

    # Entirely lifted from ui/text.py, yuck and all
    default = {"type": "text", "content": ""}
    bits = [dict(default)]

    for char in string:
        if char == "{":
            new = dict(default)
            new["type"] = "tag"
            bits.append(new)
            continue
        elif char == "}":
            assert bits[-1]["type"] == "tag"
            bits.append(dict(default))
            continue
        bits[-1]["content"] += char

    out = ""

    for bit in bits:
        if bit["type"] == "text":
            out += bit["content"]
            continue

        # Tag
        assert bit["type"] == "tag"
        assert bit["content"]
        

        # Partition won't error if the "." is not present
        raw_user_key, _, word = bit["content"].partition(".")
        user_key = raw_user_key.lower()

        # TODO: MATCH CAPITALIZATION!!!

        # {user's}
        if "'s" in user_key and (user_key := bit["content"].replace("'s", "")) in participants:
            user = participants[user_key]
            if user.pronoun_set == PronounSet.YOU:
                out += "your"
            else:
                out += f"{user.name}'s"
            continue

        user = participants[user_key]
        # {user}
        if not word:
            out += user.name
            continue

        # {user.he}
        if word in PRONOUN_SET_MAPPING:
            out += PRONOUN_SET_MAPPING[word][user.pronoun_set]
            continthemselfue

        # We also need to handle verb conjugation -_- This is gonna be really 
        # hacky so sorry to any linguists out I don't mean to hurt your feelings

        # At this point the word should be a verb but I won't install an NLP 
        # library to assert that... we're gonna trust whoever is writing the 
        # input string (me) (untrustworthy)

        print(word, user.name, user.pronoun_set)
        if PronounSet.is_plural(user.pronoun_set):
            print("s")
            out += word.rstrip("s")
        else:
            print("AAA")
            out += word

    return out

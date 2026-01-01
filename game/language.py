from __future__ import annotations

import re
import random
from enum import Enum

class Capitalization(Enum):
    # I am writing this specific class really late so if this is rly stupid dont
    # hold it against me
    UPPER = 0
    LOWER = 1
    TITLE = 2

    @classmethod
    def get(cls, string: str) -> Capitalization:
        string = "".join([c for c in string if c.isalpha()])

        if string.islower():
            return cls.LOWER
        if string.istitle():
            return cls.TITLE
        if string.isupper():
            return cls.UPPER

        print(f"!! Warn: Idk what to doooo :P with '{string}'")
        return cls.TITLE

    @staticmethod
    def to(string: str, capitalization: Capitalization) -> str:
        match capitalization:
            case Capitalization.UPPER:
                return string.upper()
            case Capitalization.LOWER:
                return string.lower()
            case Capitalization.TITLE:
                # HACK: title case makes "Claire's" into "Claire'S"
                return string.title().replace("'S", "'s")
        assert False

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
    def __init__(self, name: str, pronoun_set: PronounSet, name_format: str = "%s") -> None:
        self.true_name = name
        self.display_name = name

        self.pronoun_set = pronoun_set
        self.name_format = name_format

    @property
    def name(self) -> str:
        return self.display_name

    @property
    def pretty_name(self) -> str:
        return self.name_format % self.display_name

    def __repr__(self) -> str:
        return self.display_name

class MessagePool:
    # Lower chances of messages repeating back to back
    def __init__(self, source: list[str]) -> None:
        self.source = source
        assert self.source
        self.pool = []

    def sample(self) -> str:
        if not self.pool:
            self.pool = list(self.source)
            random.shuffle(self.pool)
        return self.pool.pop()

def third_to_base(verb: str) -> str:
    if verb == "is": return "are"
    if verb == "has": return "have"
    if verb == "does": return "do"
    
    if verb.endswith("ies"):
        return verb[:-3] + "y"

    for suffix in ["sses", "xes", "zes", "ches", "shes"]:
        if verb.endswith(suffix):
            return verb[:-2]

    if verb[-1] == "s":
        return verb[:-1]

    return verb

def evaluate_tag(raw: str, participants: dict[str, LanguageProfile]) -> str:
    # Partition won't error if the "." is not present
    raw_user_key, _, word = raw.partition(".")

    cap = Capitalization.get(raw_user_key)
    user_key = raw_user_key.lower()

    # {user's}
    if "'s" in user_key and (plural_user_key := user_key.replace("'s", "")) in participants:
        user = participants[plural_user_key]
        if user.pronoun_set == PronounSet.YOU:
            return Capitalization.to("your", cap)
        return user.name_format % Capitalization.to(f"{user.name}'s", cap)

    user = participants[user_key]
    # {user}
    if not word:
        return user.name_format % Capitalization.to(user.name, cap)

    # {user.he}
    if word in PRONOUN_SET_MAPPING:
        pronoun = PRONOUN_SET_MAPPING[word][user.pronoun_set]
        return Capitalization.to(pronoun, cap)

    # We also need to handle verb conjugation -_- This is gonna be really 
    # hacky so sorry to any linguists out I don't mean to hurt your feelings

    # At this point the word should be a verb but I won't install an NLP 
    # library to assert that... we're gonna trust whoever is writing the 
    # input string (me) (untrustworthy)
    if PronounSet.is_plural(user.pronoun_set):
        word = third_to_base(word)
    return Capitalization.to(word, cap)


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
        out += evaluate_tag(bit["content"], participants)

    return out


def indefinite_article(noun_phrase: str) -> str:
    # Function sourced from IBID with modifications for Python 2 -> 3
    # https://github.com/ibid/ibid/blob/master/ibid/utils/__init__.py

    # algorithm adapted from CPAN package Lingua-EN-Inflect-1.891 by Damian Conway
    m = re.search("\w+", noun_phrase)
    if m:
        word = m.group(0)
    else:
        return "an"

    wordi = word.lower()
    for anword in ("euler", "heir", "honest", "hono"):
        if wordi.startswith(anword):
            return "an"

    if wordi.startswith("hour") and not wordi.startswith("houri"):
        return "an"

    if len(word) == 1:
        if wordi in "aedhilmnorsx":
            return "an"
        else:
            return "a"

    if re.match(r"(?!FJO|[HLMNS]Y.|RY[EO]|SQU|"
                  r"(F[LR]?|[HL]|MN?|N|RH?|S[CHKLMNPTVW]?|X(YL)?)[AEIOU])"
                  r"[FHLMNRSX][A-Z]", word):
        return "an"

    for regex in (r"^e[uw]", r"^onc?e\b",
                    r"^uni([^nmd]|mo)","^u[bcfhjkqrst][aeiou]"):
        if re.match(regex, wordi):
            return "a"

    # original regex was /^U[NK][AIEO]?/ but that matches UK, UN, etc.
    if re.match("^U[NK][AIEO]", word):
        return "a"
    elif word == word.upper():
        if wordi[0] in "aedhilmnorsx":
            return "an"
        else:
            return "a"

    if wordi[0] in "aeio":
        return "an"

    if re.match(r"^y(b[lor]|cl[ea]|fere|gg|p[ios]|rou|tt)", wordi):
        return "an"
    else:
        return "a"

import asyncio
import pyray as rl
from typing import Optional

from game import fs

cached_sounds = {}

for path in (fs.STATIC_DIR / "sfx").glob("*.ogg"):
    print(f"[sfx] Loading {path.name}...")
    print(str(path))
    cached_sounds[path.stem] = rl.load_sound(str(path))

def play_sound(sound_str: str) -> None:
    # TODO: Some protection against crashing instantly on typos...
    rl.play_sound(cached_sounds[sound_str])

async def await_sound(
    sound_str: str,
    stop_at: Optional[float] = None
) -> None:
    sound = cached_sounds[sound_str]
    rl.play_sound(sound)

    if not sound.stream.sampleRate:
        print("[sfx] ???")
        return

    duration_secs = stop_at or (sound.frameCount / sound.stream.sampleRate)
    await asyncio.sleep(duration_secs)

    rl.stop_sound(sound)

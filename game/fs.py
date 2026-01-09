from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

SAVE_DIR = ROOT_DIR / "saves"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

STATIC_DIR = ROOT_DIR / "static"

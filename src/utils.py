# src/utils.py

from __future__ import annotations
from datetime import datetime
from pathlib import Path

def ensure_dir(path: str | Path) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)

def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

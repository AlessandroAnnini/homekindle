"""WMO → Petroff icon name, and grayscale PNG load."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import Image

_DIR = Path(__file__).resolve().parent / "icons"
_FALLBACK = "ovc"

# NOAA/Petroff names from weather-script-preprocess.svg defs.
WMO_TO_PETROFF: dict[int, str] = {
    0: "skc",
    1: "few",
    2: "sct",
    3: "ovc",
    45: "fg",
    48: "fg",
    51: "ra",
    53: "ra",
    55: "ra",
    56: "fzra",
    57: "fzra",
    61: "ra",
    63: "ra",
    65: "ra",
    66: "fzra",
    67: "fzra",
    71: "sn",
    73: "sn",
    75: "sn",
    77: "sn",
    80: "shra",
    81: "shra",
    82: "hi_shwrs",
    85: "sn",
    86: "sn",
    95: "tsra",
    96: "tsra",
    99: "scttsra",
}


def petroff_name(wmo: int) -> str:
    return WMO_TO_PETROFF.get(wmo, _FALLBACK)


@lru_cache(maxsize=64)
def petroff_png(wmo: int, size: int) -> Image.Image:
    name = petroff_name(wmo)
    path = _DIR / f"{name}.png"
    if not path.is_file():
        path = _DIR / f"{_FALLBACK}.png"
    icon = Image.open(path).convert("L")
    if icon.size != (size, size):
        icon = icon.resize((size, size), Image.Resampling.LANCZOS)
    return icon

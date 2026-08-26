"""Parse Lovelace sections YAML for the Kindle dashboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_kindle_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("kindle.yaml must be a mapping")
    views = data.get("views") or []
    if not views:
        raise ValueError("kindle.yaml needs a views list")
    return data


def packaged_layout_path() -> Path:
    return Path(__file__).with_name("kindle.yaml")

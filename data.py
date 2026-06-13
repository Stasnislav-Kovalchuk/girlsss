from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_places() -> list[dict[str, Any]]:
    path = Path(__file__).parent / "places.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_activities(places: list[dict]) -> list[dict]:
    return [p for p in places if p.get("type") == "activity"]


def get_food(places: list[dict]) -> list[dict]:
    return [p for p in places if p.get("type") == "food"]


def places_by_id(places: list[dict]) -> dict[str, dict]:
    return {p["id"]: p for p in places}

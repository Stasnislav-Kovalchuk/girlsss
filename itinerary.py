from __future__ import annotations

from datetime import datetime, timedelta


def build_timeline(places: list[dict], start_hour: int = 10) -> list[dict]:
    result = []
    current = datetime(2024, 1, 1, start_hour, 0)

    travel_gap = timedelta(minutes=40)

    for i, place in enumerate(places):
        raw = place.get("time_needed", "2 години")
        hours = _parse_hours(raw)

        entry = {
            "place": place,
            "arrive": current.strftime("%H:%M"),
            "depart": (current + timedelta(hours=hours)).strftime("%H:%M"),
        }
        result.append(entry)
        current += timedelta(hours=hours)

        if i < len(places) - 1:
            current += travel_gap

    return result


def _parse_hours(text: str) -> float:
    import re
    nums = re.findall(r"\d+", text)
    if not nums:
        return 2.0
    values = [int(n) for n in nums]
    if len(values) == 1:
        return float(values[0])
    return sum(values) / len(values)


def total_duration(timeline: list[dict]) -> str:
    if not timeline:
        return "0 годин"
    start = datetime.strptime(timeline[0]["arrive"], "%H:%M")
    end = datetime.strptime(timeline[-1]["depart"], "%H:%M")
    delta = end - start
    total_minutes = int(delta.total_seconds() / 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    if minutes:
        return f"{hours} год {minutes} хв"
    return f"{hours} годин"


def day_warning(places: list[dict]) -> str | None:
    total_dist = sum(p.get("distance_from_lviv", 0) for p in places)
    if len(places) > 4:
        return "Багато місць! Можливо, краще обрати 3–4, щоб насолодитися кожним 🌸"
    if total_dist > 400:
        return "Дуже насичена програма за відстанню — врахуйте час на дорогу 🚗"
    return None

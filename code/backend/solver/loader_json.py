"""Load immutable solver problems from JSON data."""

import json
from pathlib import Path
from typing import Any

from solver.problem import (
    Audience,
    Card,
    Day,
    Division,
    Group,
    Period,
    Placement,
    Problem,
    Room,
    RoomGroup,
    Settings,
    StudentClass,
    Teacher,
    TimeOff,
)


def _weeks(value: str | list[str]) -> tuple[str, ...]:
    if value == "all":
        return ("A", "B")
    if isinstance(value, str):
        return (value,)
    return tuple(value)


def load_problem(path: str | Path) -> tuple[Problem, list[Placement]]:
    """Load a Problem and its current placements from a JSON file."""
    with Path(path).open(encoding="utf-8") as file:
        data: dict[str, Any] = json.load(file)

    time_data = data["time"]
    allowed_starts = set(time_data["two_period_lessons_may_start_at"])
    lunch_after = time_data["lunch_break"]["after_period"]

    days = tuple(Day(id=day) for day in time_data["days"])

    periods = tuple(
        Period(
            id=item["id"],
            start=item["start"],
            end=item["end"],
            starts_block=item["id"] in allowed_starts,
            break_after=item["id"] == lunch_after,
        )
        for item in time_data["periods"]
    )

    teachers = tuple(
        Teacher(
            id=item["code"],
            name=item["name"],
            printed_as=item.get("printed_as", ""),
            tag=item.get("tag"),
            external=item.get("external", False),
            placeholder=item.get("placeholder", False),
        )
        for item in data["teachers"]
    )

    rooms = tuple(
        Room(
            id=item["name"],
            type=item["type"],
            pool=item.get("pool"),
            capacity=item.get("capacity"),
        )
        for item in data["rooms"]
    )

    room_groups = tuple(
        RoomGroup(id=pool_id, rooms=tuple(room_names))
        for pool_id, room_names in data["room_pools"].items()
    )

    classes = tuple(
        StudentClass(
            id=item["id"],
            name=item["name"],
            kind=item["kind"],
            divisions=tuple(
                Division(
                    id=f"{item['id']}-D{index}",
                    groups=tuple(Group(id=group, name=group) for group in division),
                )
                for index, division in enumerate(item.get("divisions", []), start=1)
            ),
            size=item.get("size"),
        )
        for item in data["classes"]
    )

    cards: list[Card] = []
    placements: list[Placement] = []

    for item in data["lessons"]:
        current = item.get("current")
        room_pool = item["room_pool"]

        room_group = room_pool if room_pool in data["room_pools"] else None
        exact_room = current.get("room") if room_pool == "FIXED" and current else None

        fixed_time = item.get("fixed_time", False)

        cards.append(
            Card(
                id=item["id"],
                course=item["course"],
                length_periods=item["length_periods"],
                weeks=_weeks(item["weeks"]),
                teachers=tuple(item.get("teachers", [])),
                audiences=tuple(
                    Audience(
                        class_id=audience["class"],
                        group_id=audience.get("group"),
                    )
                    for audience in item.get("audience", [])
                ),
                room_group=room_group,
                exact_room=exact_room,
                allow_same_day=item.get("is_project_slot", False),
                fixed_day=current["day"] if fixed_time and current else None,
                fixed_period=current["start_period"] if fixed_time and current else None,
                assumption=item.get("assumption"),
                notes=tuple(item.get("notes", [])),
            )
        )

        if current:
            placements.append(
                Placement(
                    card_id=item["id"],
                    day=current["day"],
                    start_period=current["start_period"],
                    room=current.get("room"),
                )
            )

    time_off: list[TimeOff] = []
    allowed_days = (
        data.get("assumed_constraints", {}).get("external_teacher_allowed_days", {}).get("days", {})
    )

    for teacher in teachers:
        if teacher.external and teacher.id in allowed_days:
            available = set(allowed_days[teacher.id])
            for day in time_data["days"]:
                if day not in available:
                    time_off.append(
                        TimeOff(
                            entity_type="teacher",
                            entity_id=teacher.id,
                            day=day,
                        )
                    )

    problem = Problem(
        days=days,
        periods=periods,
        teachers=teachers,
        rooms=rooms,
        room_groups=room_groups,
        classes=classes,
        cards=tuple(cards),
        time_off=tuple(time_off),
        settings=Settings(),
    )

    return problem, placements

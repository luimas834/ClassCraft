"""Immutable data structures used by the ClassCraft solver."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Day:
    id: str
    active: bool = True


@dataclass(frozen=True)
class Period:
    id: int
    start: str
    end: str
    starts_block: bool = False
    break_after: bool = False


@dataclass(frozen=True)
class Teacher:
    id: str
    name: str
    printed_as: str = ""
    tag: str | None = None
    external: bool = False
    placeholder: bool = False


@dataclass(frozen=True)
class Room:
    id: str
    type: str
    pool: str | None = None
    capacity: int | None = None
    active: bool = True


@dataclass(frozen=True)
class RoomGroup:
    id: str
    rooms: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Group:
    id: str
    name: str
    size: int | None = None


@dataclass(frozen=True)
class Division:
    id: str
    groups: tuple[Group, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class StudentClass:
    id: str
    name: str
    kind: str
    divisions: tuple[Division, ...] = field(default_factory=tuple)
    size: int | None = None


@dataclass(frozen=True)
class Audience:
    class_id: str
    group_id: str | None = None


@dataclass(frozen=True)
class Card:
    id: str
    course: str
    length_periods: int
    weeks: tuple[str, ...]
    teachers: tuple[str, ...]
    audiences: tuple[Audience, ...]
    room_group: str | None = None
    exact_room: str | None = None
    allow_same_day: bool = False
    fixed_day: str | None = None
    fixed_period: int | None = None
    lock_day: str | None = None
    lock_period: int | None = None
    lock_room: str | None = None
    assumption: str | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class TimeOff:
    entity_type: str
    entity_id: str
    day: str
    period: int | None = None
    week: str | None = None
    preferred: bool = False


@dataclass(frozen=True)
class Settings:
    h8: bool = True
    h9: bool = True
    h10: bool = True
    h12: bool = False
    s1_weight: int = 3
    s2_weight: int = 2
    s3_weight: int = 1
    s4_weight: int = 2
    max_consecutive: int = 3


@dataclass(frozen=True)
class Placement:
    card_id: str
    day: str
    start_period: int
    room: str | None = None
    week: str | None = None


@dataclass(frozen=True)
class Problem:
    days: tuple[Day, ...]
    periods: tuple[Period, ...]
    teachers: tuple[Teacher, ...]
    rooms: tuple[Room, ...]
    room_groups: tuple[RoomGroup, ...]
    classes: tuple[StudentClass, ...]
    cards: tuple[Card, ...]
    time_off: tuple[TimeOff, ...] = field(default_factory=tuple)
    settings: Settings = field(default_factory=Settings)
    weeks: tuple[str, ...] = ("A", "B")

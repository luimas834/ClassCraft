"""Checks a finished routine against the hard rules with plain loops.

The validator is the referee for the solver. It never imports OR-Tools, so a
mistake in the solver's model cannot hide a clash from this check.
"""

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations

from solver.problem import Card, Placement, Problem, Settings

# What one card claims of one class in one slot: the card id and the group, if any.
_Seat = tuple[str, str | None]


@dataclass(frozen=True)
class Violation:
    """One broken hard rule, with a sentence a committee member can read."""

    rule: str
    card_ids: tuple[str, ...]
    day: str | None
    period: int | None
    text: str


@dataclass(frozen=True)
class _Grid:
    """The period grid in the shape the checks need."""

    active_days: frozenset[str]
    periods: frozenset[int]
    block_starts: frozenset[int]
    break_after: frozenset[int]


def validate(
    problem: Problem,
    placements: list[Placement],
    settings: Settings | None = None,
) -> list[Violation]:
    """Return every broken hard rule of H1 to H9, in rule order.

    `settings` says which switchable rules are on; it defaults to the settings
    that came with the problem.
    """
    cards = {card.id: card for card in problem.cards}
    placed = [item for item in placements if item.card_id in cards]

    found: list[Violation] = []
    found += _check_h1(problem, placed)
    found += _check_h2(problem, placed, cards)
    found += _check_h3(problem, placed, cards)
    found += _check_h4(problem, placed, cards)
    found += _check_h5(problem, placed, cards)
    return sorted(found, key=lambda item: (item.rule, item.card_ids))


def _check_h1(problem: Problem, placed: list[Placement]) -> list[Violation]:
    """H1: every card is placed exactly once."""
    counts: dict[str, int] = defaultdict(int)
    for item in placed:
        counts[item.card_id] += 1

    found: list[Violation] = []
    for card in problem.cards:
        times = counts[card.id]
        if times == 1:
            continue
        audience = _audience_label(problem, card)
        if times == 0:
            text = f"{card.course} for {audience} is not placed."
        else:
            text = f"{card.course} for {audience} is placed more than once."
        found.append(Violation("H1", (card.id,), None, None, text))
    return found


def _check_h2(
    problem: Problem,
    placed: list[Placement],
    cards: dict[str, Card],
) -> list[Violation]:
    """H2: a long lesson starts a block and never runs across a break."""
    grid = _read_grid(problem)

    found: list[Violation] = []
    for item in placed:
        card = cards[item.card_id]
        if not _slot_is_impossible(grid, card, item):
            continue
        audience = _audience_label(problem, card)
        found.append(
            Violation(
                "H2",
                (card.id,),
                item.day,
                item.start_period,
                f"{card.course} for {audience} cannot start at period {item.start_period}.",
            )
        )
    return found


def _slot_is_impossible(grid: _Grid, card: Card, placement: Placement) -> bool:
    """No lesson of this length may start here, whatever else is placed."""
    if placement.day not in grid.active_days:
        return True
    covered = _covered_periods(card, placement)
    if any(period not in grid.periods for period in covered):
        return True
    if card.length_periods > 1 and placement.start_period not in grid.block_starts:
        return True
    # The last period of a lesson may be followed by a break; an earlier one may not.
    return any(period in grid.break_after for period in covered[:-1])


def _read_grid(problem: Problem) -> _Grid:
    """Read the days and periods once, so the checks do not walk them again."""
    return _Grid(
        active_days=frozenset(day.id for day in problem.days if day.active),
        periods=frozenset(period.id for period in problem.periods),
        block_starts=frozenset(period.id for period in problem.periods if period.starts_block),
        break_after=frozenset(period.id for period in problem.periods if period.break_after),
    )


def _covered_periods(card: Card, placement: Placement) -> tuple[int, ...]:
    """The periods a card sits in: its start period and the ones after it."""
    start = placement.start_period
    return tuple(range(start, start + card.length_periods))


def _check_h3(
    problem: Problem,
    placed: list[Placement],
    cards: dict[str, Card],
) -> list[Violation]:
    """H3: a teacher takes one lesson at a time."""
    busy: dict[tuple[str, str, str, int], list[Placement]] = defaultdict(list)
    for item in placed:
        card = cards[item.card_id]
        for teacher in card.teachers:
            for week in _weeks_of(card, item):
                for period in _covered_periods(card, item):
                    busy[(teacher, week, item.day, period)].append(item)

    found: list[Violation] = []
    for (teacher, _week, day, period), items in busy.items():
        for one, two in _card_pairs(cards, items):
            found.append(
                Violation(
                    "H3",
                    (one.id, two.id),
                    day,
                    period,
                    f"{_teacher_label(problem, teacher)} teaches {one.course} and "
                    f"{two.course} at the same time ({day}, period {period}).",
                )
            )
    return _earliest_per_pair(problem, found)


def _weeks_of(card: Card, placement: Placement) -> tuple[str, ...]:
    """The weeks a placement runs in. An alternate-week card runs in one week."""
    if placement.week is None:
        return card.weeks
    return tuple(week for week in card.weeks if week == placement.week)


def _card_pairs(cards: dict[str, Card], items: list[Placement]) -> list[tuple[Card, Card]]:
    """Every pair of different cards sharing one slot, in a fixed order."""
    unique = sorted({item.card_id for item in items})
    return [(cards[first], cards[second]) for first, second in combinations(unique, 2)]


def _earliest_per_pair(problem: Problem, found: list[Violation]) -> list[Violation]:
    """Keep one sentence per pair of cards: the earliest slot they share."""
    day_order = {day.id: index for index, day in enumerate(problem.days)}
    best: dict[tuple[str, tuple[str, ...]], Violation] = {}
    for item in found:
        key = (item.rule, item.card_ids)
        current = best.get(key)
        if current is None or _slot_order(day_order, item) < _slot_order(day_order, current):
            best[key] = item
    return list(best.values())


def _slot_order(day_order: dict[str, int], item: Violation) -> tuple[int, int]:
    """How early in the week a violation sits, so one pair gives one sentence."""
    return (day_order.get(item.day, len(day_order)), item.period or 0)


def _check_h4(
    problem: Problem,
    placed: list[Placement],
    cards: dict[str, Card],
) -> list[Violation]:
    """H4: a room holds one lesson at a time."""
    busy: dict[tuple[str, str, str, int], list[Placement]] = defaultdict(list)
    for item in placed:
        if item.room is None:
            continue
        card = cards[item.card_id]
        for week in _weeks_of(card, item):
            for period in _covered_periods(card, item):
                busy[(item.room, week, item.day, period)].append(item)

    found: list[Violation] = []
    for (room, _week, day, period), items in busy.items():
        for one, two in _card_pairs(cards, items):
            found.append(
                Violation(
                    "H4",
                    (one.id, two.id),
                    day,
                    period,
                    f"{room} holds {one.course} and {two.course} at the same time "
                    f"({day}, period {period}).",
                )
            )
    return _earliest_per_pair(problem, found)


def _check_h5(
    problem: Problem,
    placed: list[Placement],
    cards: dict[str, Card],
) -> list[Violation]:
    """H5: a student group attends one lesson at a time."""
    division_of = _division_of_group(problem)
    busy: dict[tuple[str, str, str, int], list[_Seat]] = defaultdict(list)
    for item in placed:
        card = cards[item.card_id]
        for audience in card.audiences:
            for week in _weeks_of(card, item):
                for period in _covered_periods(card, item):
                    key = (audience.class_id, week, item.day, period)
                    busy[key].append((item.card_id, audience.group_id))

    found: list[Violation] = []
    for (class_id, _week, day, period), seats in busy.items():
        for first, second in _seat_pairs(seats):
            if not _seats_clash(division_of, class_id, first[1], second[1]):
                continue
            one, two = cards[first[0]], cards[second[0]]
            found.append(
                Violation(
                    "H5",
                    (one.id, two.id),
                    day,
                    period,
                    f"{_class_label(problem, class_id)} has {one.course} and "
                    f"{two.course} at the same time ({day}, period {period}).",
                )
            )
    return _earliest_per_pair(problem, found)


def _seat_pairs(seats: list[_Seat]) -> list[tuple[_Seat, _Seat]]:
    """Every pair of seats of one class in one slot that belongs to two cards."""
    unique = sorted(set(seats), key=lambda seat: (seat[0], seat[1] or ""))
    return [(one, two) for one, two in combinations(unique, 2) if one[0] != two[0]]


def _seats_clash(
    division_of: dict[tuple[str, str], str],
    class_id: str,
    first_group: str | None,
    second_group: str | None,
) -> bool:
    """Two lessons of one class clash unless they are two groups of one division."""
    if first_group is None or second_group is None:
        return True
    if first_group == second_group:
        return True
    first = division_of.get((class_id, first_group))
    second = division_of.get((class_id, second_group))
    if first is None or second is None:
        return True
    return first != second


def _division_of_group(problem: Problem) -> dict[tuple[str, str], str]:
    """Which division each group belongs to, for every class."""
    return {
        (student_class.id, group.id): division.id
        for student_class in problem.classes
        for division in student_class.divisions
        for group in division.groups
    }


def _teacher_label(problem: Problem, teacher_id: str) -> str:
    """The short code a routine prints for a teacher, for example `KH`."""
    for teacher in problem.teachers:
        if teacher.id == teacher_id:
            return teacher.printed_as or teacher.name
    return teacher_id


def _class_label(problem: Problem, class_id: str) -> str:
    """The name a routine prints for a class."""
    for student_class in problem.classes:
        if student_class.id == class_id:
            return student_class.name
    return class_id


def _audience_label(problem: Problem, card: Card) -> str:
    """Who sits in a lesson: the classes, with the group when there is one."""
    if not card.audiences:
        return "no class"
    parts = []
    for audience in card.audiences:
        name = _class_label(problem, audience.class_id)
        parts.append(f"{name} {audience.group_id}" if audience.group_id else name)
    return ", ".join(parts)

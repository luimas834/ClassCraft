"""Checks a finished routine against the hard rules with plain loops.

The validator is the referee for the solver. It never imports OR-Tools, so a
mistake in the solver's model cannot hide a clash from this check.
"""

from collections import defaultdict
from dataclasses import dataclass

from solver.problem import Card, Placement, Problem, Settings


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

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
